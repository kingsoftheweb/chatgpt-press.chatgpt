import json

import quart
import quart_cors
from quart import request, redirect
import requests
from ast import literal_eval
import datetime
from dateutil.parser import parse
import jwt
from functools import wraps
import uuid
import re

from globals import _SECRET, _CONF

from src.Posts import Posts
from src.Plugins import Plugins

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")


def genAuth(site=False):
    if (not site): return noSiteException()
    uid = str(uuid.uuid1())
    try:
        r = requests.get(site)
        if (r.status_code != 200):  return {"error": "Please check your web address. It seems invalid."}
    except:
        return {"error": "Please check your web address. It seems invalid."}
    if (requests.get(site + "/authenticate-chatgptpress").status_code == 200):
        login_url = site + "/authenticate-chatgptpress?redirect_to=http://localhost:5003/login/" + uid
        _CONF[uid] = {"status": True, "site": site}
        sid = jwt.encode({"uid": uid, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=85)}, _SECRET,
                         algorithm="HS256")
        return {
            "uid": sid,
            "action": "You need to login manually. chatGPT will show login link: " + login_url
        }
    else:
        return {
            "error": "chatgptpress plugin not found in your website. please install the plugin and come back again."}


def indigest(token):
    try:
        return jwt.decode(token, _SECRET, verify_exp=True, algorithms=["HS256"])
    except:
        return {"error": "The request session has been expired. please give your wp site address to start again."}


def noSiteException():
    return {"error": "provide you wp site address to continue."}


def validSite(site):
    site = site.replace("https://", "")
    site = site.replace("http://", "")
    site = "https://" + site
    return site


def logged():
    def wrapper(func):
        @wraps(func)
        async def wrapped(*args, **kwargs):
            token = kwargs["token"]
            try:
                ind = indigest(token)
                uid = ind["uid"]
                usr = ind["user"]
                password = ind["pass"]
                if (uid and usr and password):
                    print("ok")
                else:
                    return {
                        "error": "The request session has been expired. please give your wp site address to start again."}
            except:
                return {
                    "error": "The request session has been expired. please give your wp site address to start again."}
            return await func(*args, **kwargs)

        return wrapped

    return wrapper


@app.post("/token")
async def get_token_from_chat():
    uid = ""
    try:
        uid = indigest(request.args.get('uid'))["uid"]
    except:
        return {"error": "login link expired", "action": "Get a new login link from /login"}
    inConf = _CONF.get(uid)
    if (not inConf): return {"error": "login link expired", "action": "Get a new login link from /login"}
    status = inConf.get("status")
    token = inConf.get("token")
    if (status and not token): return genAuth()
    if (status and token): return {"token": inConf["token"]}
    if (not status): return {"error": "Not registed yet"}
    return genAuth()


@app.post("/login")
async def login_to_chat():
    return genAuth(validSite(request.args.get("site")))


@app.get("/login/<string:uid>")
async def login_to_site(uid):
    url = "/wp-json/wp/v2/users/me"
    if (not _CONF.get(uid)): return "Bad or illegal Request"
    try:
        auth = (request.args.get("username"), request.args.get("appPassword"))
        r = requests.post(_CONF.get(uid)["site"] + url, auth=auth).json()
        if (r["id"]): status = "Login successfull, please go back to GPT conversation."
        print(r["id"])
        json_payload = {
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=85),
            "site": _CONF.get(uid)["site"],
            "user": request.args.get("username"),
            "pass": request.args.get("appPassword"),
            "uid": uid,
            "author": str(r["id"])
        }
        _CONF[uid]["token"] = jwt.encode(json_payload, _SECRET, algorithm="HS256")
    except:
        print("error login")
        return """
            <script>
                alert("Something is wrong!!! Please try again later...");
                window.close();
            </script>
        """
    if (_CONF.get(uid)):
        return """
            <script>
                alert("Login successfull. Please go back to chatGPT and continue your conversation.");
                window.close();
            </script>
        """
    else:
        return """
        <script>
                alert("Something is wrong!!! Please try again later...");
                window.close();
            </script>
        """


########################
# POSTS ################
########################
@app.get("/posts/<string:token>")
async def get_posts(token):
    res = await Posts().get_posts(token)
    return quart.Response(response=res, status=200)


@app.post("/addPost/<string:token>")
@logged()
async def add_new_post(token):
    res = await Posts().add_new(token)
    return quart.Response(response=res, status=200)


@app.post("/updatePost/<string:token>")
@logged()
async def update_post(token):
    res = await Posts().update(token)
    return quart.Response(response=res, status=200)


@app.post("/deletePost/<string:token>/<string:postId>")
@logged()
async def delete_post(token, postId):
    res = await Posts().delete(token, postId)
    return quart.Response(response=res, status=200)


########################
# PLUGINS ##############
########################
@app.post("/findPlugin/<string:token>/<string:keyword>")
@logged()
async def find_plugin(token, keyword):
    res = Plugins.find_plugin(token, keyword)
    return quart.Response(response=json.dumps(res), status=200)


@app.post("/installPlugin/<string:token>/<string:slug>")
@logged()
async def install_plugin(token, slug):
    token = indigest(token)
    url = token["site"] + "/wp-json/chatgptpress/v1/plugins/install"
    r = requests.post(url, json={"slug": slug}, auth=(token["user"], token["pass"]))
    res = r.json()
    return quart.Response(response=json.dumps(res), status=200)


@app.post("/debug/<string:token>")
@logged()
async def find_bug(token):
    token = indigest(token)
    url = token["site"] + "/wp-json/chatgptpress/v1/debuglog/debug"
    r = requests.get(url, auth=(token["user"], token["pass"]))
    pList = r.json()
    resList = []
    counter = 0
    for p in pList:
        counter += 1
        p.pop("date")
        p.pop("time")
        p.pop("timeZone")
        resList.append(p)
        if (counter >= 50): break
    res = {"action": "chatGPT will suggest how to fix this errors", "plugins": resList}
    return quart.Response(response=json.dumps(res), status=200)


@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")


@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")


def main():
    app.run(debug=True, host="0.0.0.0", port=5003)


if __name__ == "__main__":
    main()

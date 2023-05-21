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

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")
_SECRET = "THIS IS SUPER SECRET"
_CONF = {}

def genAuth(site):
    uid = str(uuid.uuid1())
    if(requests.get(site+"/authenticate-chatgptpress").status_code==200):
        login_url = site+"/authenticate-chatgptpress?redirect_to=http://localhost:5003/login/"+uid
        _CONF[uid]={"status":True,"site":site}
        sid = jwt.encode({"uid":uid,"exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=85)}, _SECRET, algorithm="HS256")
        return {
            "uid":sid,
            "action":"You need to login manually. chatGPT will show login link: "+login_url
            }
    else:
        return{"error":"chatgptpress plugin not found in your website. please install the plugin and come back again."}

def indigest(token):
    try:
        return jwt.decode(token, _SECRET, verify_exp=True, algorithms=["HS256"])
    except:
        return {"error":"The request session has been expired. please give your wp site address to start again."}

def logged():
    def wrapper(func):
        @wraps(func)
        async def wrapped(*args, **kwargs):
            token = kwargs["token"]
            try:
                ind=indigest(token)
                uid= ind["uid"]
                usr=ind["user"]
                password = ind["pass"]
                if(uid and usr and password):
                    print("ok")
                else:
                   return {"error":"The request session has been expired. please give your wp site address to start again."}
            except:
                return {"error":"The request session has been expired. please give your wp site address to start again."}
            return await func(*args, **kwargs)
        return wrapped
    return wrapper


 

#("futrx","D6Jt ZbFV yrJ8 QI7w uYIy VQMS")
# @app.post("/auth")
# async def auth_to_wp():
#     url = "https://chatgpt.futrx.ca/wp-json/wp/v2/users/me"
#     global _AUTH
#     _AUTH = (request.args.get('user'),request.args.get('password'))
#     r = requests.post(url, auth = _AUTH)
#     return quart.Response(response=json.dumps(r.json()), status=200)


# @app.post("/auth")
# async def auth_to_wp():
#     d = await request.get_data()
#     d = json.loads(d.decode("utf-8"))
#     url = "https://chatgpt.futrx.ca/wp-json/wp/v2/users/me"
#     uid = d["uid"]
#     if(not _CONF.get(uid)):return "Bad or illegal Request"
#     try:
#         auth = (d["user"],d["password"])
#         r = requests.post(url, auth = auth).json()
#         if(r["id"]):status="Login successfull, please go back to GPT conversation."
#         print(r["id"])
#         json_payload = {
#             "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=85),
#             "user": d["user"], 
#             "pass":d["password"],
#             "uid":uid,
#             "author":str(r["id"])
#         }
#         _CONF[uid]["token"]=jwt.encode(json_payload, _SECRET, algorithm="HS256")
#     except:
#         print("error login")
#     if(_CONF.get(uid)):
#         return quart.Response(response=json.dumps({"status":"ok"}), status=200)
#     else:
#         return quart.Response(response="error", status=300)
    


@app.post("/token")
async def get_token_from_chat():
    uid = ""
    try:
        uid = indigest(request.args.get('uid'))["uid"]
    except:
        return  {"error":"login link expired","action":"Get a new login link from /login"}
    inConf = _CONF.get(uid)
    if(not inConf): return  {"error":"login link expired","action":"Get a new login link from /login"}
    status = inConf.get("status")
    token = inConf.get("token")
    if(status and not token): return genAuth()
    if(status and token):return {"token":inConf["token"]}
    if(not status): return {"error":"Not registed yet"}
    return genAuth()

@app.post("/login")
async def login_to_chat():
    return genAuth(request.args.get("site"))

@app.get("/login/<string:uid>")
async def login_to_site(uid):
    url = "/wp-json/wp/v2/users/me"
    if(not _CONF.get(uid)):return "Bad or illegal Request"
    try:
        auth = (request.args.get("username"),request.args.get("appPassword"))
        r = requests.post(_CONF.get(uid)["site"]+url, auth = auth).json()
        if(r["id"]):status="Login successfull, please go back to GPT conversation."
        print(r["id"])
        json_payload = {
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=85),
            "site": _CONF.get(uid)["site"],
            "user": request.args.get("username"), 
            "pass": request.args.get("appPassword"),
            "uid":uid,
            "author":str(r["id"])
        }
        _CONF[uid]["token"]=jwt.encode(json_payload, _SECRET, algorithm="HS256")
    except:
        print("error login")
        return """
            <script>
                alert("Something is wrong!!! Please try again later...");
                window.close();
            </script>
        """
    if(_CONF.get(uid)):
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
    

# @app.get("/auth")
# async def login_form():
#     form = """
#     <form action="/auth" method="post">
#         <label for="user">User Name:</label><br>
#         <input id="user" type="text" name="user" value=""><br>

#         <label for="password">Password:</label><br>
#         <input id="password" type="password" name="password"><br><br>

#         <input type="button" id="login" value="Submit">
#     </form>
#     <script>
#         const btn = document.getElementById("login");
#         btn.addEventListener("click",function(){
#            fetch("/auth",{
#                 method:"POST",
#                 body: JSON.stringify({
#                     "password":document.getElementById("password").value,
#                     "user":document.getElementById("user").value,
#                     "uid":location.href.split("sid=")[1]
#                     })
#             }).then(async (res)=>{
#                 const stat = await res.json()
#                 if(stat){
#                     alert("successfully log in, please go to chatGPT");
#                     window.close();
#                 }else{
#                     alert("Wrong user or password")
#                 }
#             }).catch((error) => {
#                  alert("Wrong user or password")
#                 });
#         })
#     </script>
#     """
#     return form

@app.get("/posts/<string:token>")
async def get_posts(token):
    token = indigest(token)
    if(token.get("error")):return token
    url = token["site"]+"/wp-json/wp/v2/posts?"
    if(request.args.get('postId')):
        url = token["site"]+"/wp-json/wp/v2/posts/"+request.args.get('postId')
        print(url)
        r = requests.get(url)
        return quart.Response(response=json.dumps(r.json()), status=200)
    if(request.args.get('postType')):url = token["site"]+'/wp-json/wp/v2/'+request.args.get('postType')+"?"  
    url+="_fields=id,date,link&per_page=10"
    after = request.args.get('afterDate')
    if(after):url += "&after="+parse(after).isoformat()
    before = request.args.get('beforeDate')
    if(before):url += "&before="+parse(before).isoformat()
    r = requests.get(url)
    return quart.Response(response=json.dumps(r.json()), status=200)


@app.post("/addPost/<string:token>")
@logged()
async def add_new_post(token):
    token = indigest(token)
    url = token["site"]+"/wp-json/wp/v2/posts"
    raw_data = (await request.body)
    data = {}
    d = {"title":"","content":"","author":""}
    try:
        d = literal_eval(raw_data.decode('utf-8'))
    except:
        print("raw_data Error")
    author = token["author"]
    data = {
        "title":d.get("title"),
        "content":d.get("content"),
        "status":"draft",
        "author":int(author)
    }
    
    if(d.get("postType")):data["type"]=d["postType"]
    auth = (token["user"],token["pass"])
    r = requests.post(url, data = data, auth = auth)
    res = "Post Error"
    if(r.json()):res=json.dumps(r.json())
    return quart.Response(response=res, status=200)



@app.post("/updatePost/<string:token>")
@logged()
async def update_existed_post(token):
    token = indigest(token)
    url = token["site"]+"/wp-json/wp/v2/posts/"+request.args.get('post_id')
    data = {
        "title":request.args.get('title')
    }
    r = requests.post(url, data = data, auth = (token["user"],token["pass"]))
    return quart.Response(response=json.dumps(r.json()), status=200)

@app.post("/deletePost/<string:token>/<string:postId>")
@logged()
async def delete_post(token,postId):
    token = indigest(token)
    url = token["site"]+"/wp-json/wp/v2/posts/"+postId
    r = requests.delete(url, auth = (token["user"],token["pass"]))
    return quart.Response(response=json.dumps(r.json()), status=200)


@app.post("/findPlugin/<string:token>/<string:keyword>")
@logged()
async def find_plugin(token,keyword):
    token = indigest(token)
    url = token["site"]+"/wp-json/chatgptpress/v1/plugins/search"
    r = requests.post(url, json={"keyword":keyword}, auth = (token["user"],token["pass"]))
    pList = r.json()
    resList = []
    counter = 0
    for p in pList:
        counter+=1
        p.pop("short_description")
        resList.append(p)
        if(counter>=50): break
    res = {"action":"chatGPT will find and suggest best plugin to install as user's expectation and comapre among them and", "plugins":resList}
    return quart.Response(response=json.dumps(res), status=200)


@app.post("/installPlugin/<string:token>/<string:slug>")
@logged()
async def install_plugin(token,slug):
    token = indigest(token)
    url = token["site"]+"/wp-json/chatgptpress/v1/plugins/install"
    r = requests.post(url, json={"slug":slug}, auth = (token["user"],token["pass"]))
    res = r.json()
    return quart.Response(response=json.dumps(res), status=200)


@app.post("/debug/<string:token>")
@logged()
async def find_bug(token):
    token = indigest(token)
    url = token["site"]+"/wp-json/chatgptpress/v1/debuglog/debug"
    r = requests.get(url, auth = (token["user"],token["pass"]))
    pList = r.json()
    resList = []
    counter = 0
    for p in pList:
        counter+=1
        p.pop("date")
        p.pop("time")
        p.pop("timeZone")
        resList.append(p)
        if(counter>=50): break
    res = {"action":"chatGPT will suggest how to fix this errors", "plugins":resList}
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

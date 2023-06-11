import quart
import quart_cors
from quart import request
from functools import wraps
import json
from src.Posts import Posts
from globals import _SERVICE_AUTH_KEY

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")


####################
# Plugin Configs ###
####################
@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open(".well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")


@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")


@app.get("/legal")
async def legal_docs():
    host = request.headers['Host']
    with open(".well-known/legal.html") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/html")

########################
# plugin service level auth ################
########################
def assert_auth_header(req):
    if(req.headers.get("Authorization", None) == f"Bearer {_SERVICE_AUTH_KEY}"):
        return True
    else:
        return False
   
 
########################
# POSTS ################
########################
@app.get("/posts")
async def get_posts():
    if(not assert_auth_header(quart.request)): return quart.Response(response=json.dumps({"error":"Auth is invalid for the plugin"}), status=200)
    res = await Posts().get_posts()
    return quart.Response(response=res, status=200)


@app.post("/posts")
async def get_post_details():
    if(not assert_auth_header(quart.request)):return quart.Response(response=json.dumps({"error":"Auth is invalid for the plugin"}), status=200)
    res = await Posts().get_post_details()
    return quart.Response(response=res, status=200)


def main():
    app.run(debug=True, host="0.0.0.0", port=5003)


if __name__ == "__main__":
    main()

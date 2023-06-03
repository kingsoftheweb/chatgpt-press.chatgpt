import quart
import quart_cors
from quart import request
from functools import wraps

from src.helpers import indigest, validate_site

from src.Authenticate import Authenticate
from src.Posts import Posts


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
# Authentication #######
########################
@app.post("/token")
async def get_token_from_chat():
    return Authenticate().get_token()


@app.post("/login")
async def login_to_chat():
    return Authenticate().start(validate_site(request.args.get("site")))

def req_validator():
    def wrapper(func):
        @wraps(func)
        async def wrapped(*args, **kwargs):
            token = kwargs["token"]
            ind = indigest(token)
            if ind.get("error"): return {"error":"Please start by giving your site address so we can proceed."}
            try:
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


########################
# POSTS ################
########################
@app.get("/posts/<string:token>")
@req_validator()
async def get_posts(token):
    res = await Posts().get_posts(token)
    return quart.Response(response=res, status=200)


@app.post("/posts/<string:token>")
@req_validator()
async def get_post_details(token):
    res = await Posts().get_post_details(token)
    return quart.Response(response=res, status=200)


@app.post("/addPost/<string:token>")
@req_validator()
async def add_new_post(token):
    res = await Posts().add_new(token)
    return quart.Response(response=res, status=200)


@app.post("/updatePost/<string:token>")
@req_validator()
async def update_post(token):
    res = await Posts().update(token)
    return quart.Response(response=res, status=200)


@app.post("/deletePost/<string:token>/<string:postId>")
@req_validator()
async def delete_post(token, postId):
    res = await Posts().delete(token, postId)
    return quart.Response(response=res, status=200)

def main():
    app.run(debug=True, host="0.0.0.0", port=5003)


if __name__ == "__main__":
    main()

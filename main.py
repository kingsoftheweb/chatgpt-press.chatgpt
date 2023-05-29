import json
import quart
import quart_cors
from quart import request
from functools import wraps

from globals import _CONF
from src.helpers import indigest, validate_site, wp_info

from src.Authenticate import Authenticate
from src.Posts import Posts
from src.Plugins import Plugins
from src.Debug import Debug

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


@app.get("/login/<string:uid>")
async def login_to_wordpress(uid):
    await Authenticate().login_to_wordpress(uid)
    if _CONF.get(uid):
        return """
            <h6>Login successfull. Please go back to chatGPT and continue your conversation.</h6>
            <script>
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


########################
# POSTS ################
########################
@app.get("/posts/<string:token>")
async def get_posts(token):
    res = await Posts().get_posts(token)
    return quart.Response(response=res, status=200)


@app.post("/posts/<string:token>")
async def get_post_details(token):
    res = await Posts().get_post_details(token)
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
    res = await Plugins().find(token, keyword)
    return quart.Response(response=json.dumps(res), status=200)


@app.post("/installPlugin/<string:token>/<string:slug>")
@logged()
async def install_plugin(token, slug):
    try:
        res = await Plugins().install(token, slug)
        return quart.Response(response=res, status=200)
    except json.decoder.JSONDecodeError:
        error_message = "Error: Failed to parse JSON response"
        return quart.Response(response=error_message, status=500)


########################
# WP INFO ##############
########################
@app.post("/wpInfo/<string:token>")
@logged()
async def get_wp_info(token):
    return quart.Response(response=json.dumps(wp_info()), status=200)


########################
# DEBUG ################
########################
@app.post("/debug/<string:token>")
@logged()
async def debug_list(token):
    res = Debug().list(token)
    return quart.Response(response=res, status=200)


def main():
    app.run(debug=True, host="0.0.0.0", port=5003)


if __name__ == "__main__":
    main()

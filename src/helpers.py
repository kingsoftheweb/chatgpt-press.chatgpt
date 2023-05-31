import jwt
from globals import _SECRET
import requests


def indigest(token):
    try:
        return jwt.decode(token, _SECRET, verify_exp=True, algorithms=["HS256"])
    except:
        return {"error": "The request session has been expired. please give your wp site address to start again."}


def no_site_exception():
    return {"error": "provide you wp site address to continue."}


def login_error_exception():
    return {"error": "login failed. please try again."}


def validate_site(site_url):
    # return a valid https url
    if site_url.startswith("http://"):
        site_url = site_url.replace("http://", "https://")
    elif not site_url.startswith("https://"):
        site_url = "https://" + site_url
    return site_url


def plugin_info():
    req = requests.get("https://chatgpt.futrx.ca/wp-json/chatgptpress/v1/info/get")
    allInfo = req.json()
    activate_plugins = {}
    if (allInfo.get("active_plugins")):
        for p in allInfo["active_plugins"]:
            slug = p.split("/")[0]
            activate_plugins[slug] = True
    return {"wordpress_version": allInfo.get("wordpress_version"),
            "activate_plugins": activate_plugins}


def wp_info():
    req = requests.get("https://chatgpt.futrx.ca/wp-json/chatgptpress/v1/info/get")
    return req.json()


def valid_post_type(postType):
    if postType == "post" or postType is None:
        return "posts"
    return postType

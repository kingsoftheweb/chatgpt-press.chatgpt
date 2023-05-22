import jwt
from quart import request, redirect
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


def validate_site(site):
    site = site.replace("https://", "")
    site = site.replace("http://", "")
    site = "https://" + site
    return site

def plugin_info():
    req = requests.get("https://chatgpt.futrx.ca/wp-json/chatgptpress/v1/info/get")
    allInfo = req.json()
    activate_plugins = {}
    if(allInfo.get("active_plugins")):
        for p in allInfo["active_plugins"]:
            slug = p.split("/")[0]
            activate_plugins[slug]=True
    
    return {"wordpress_version":allInfo.get("wordpress_version"),
            "activate_plugins":activate_plugins}


def valid_post_type(postType):
    if(postType=="post"): 
        postType = "posts"
    return postType
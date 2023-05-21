import jwt
from quart import request, redirect
from globals import _SECRET


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

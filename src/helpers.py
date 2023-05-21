import jwt
from quart import request, redirect
from globals import _SECRET


def indigest(token):
    try:
        return jwt.decode(token, _SECRET, verify_exp=True, algorithms=["HS256"])
    except:
        return {"error": "The request session has been expired. please give your wp site address to start again."}

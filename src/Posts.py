import json

import requests
from quart import request
from ast import literal_eval

from src.helpers import indigest


class Posts:
    """
    Posts class

    This class is used to handle all the requests related to posts.
    Currently, supports:
        - Adding new posts 'add_new_post()'
    """

    async def add_new_post(self, token):
        token = indigest(token)
        url = token["site"] + "/wp-json/wp/v2/posts"
        raw_data = (await request.body)
        d = {"title": "", "content": "", "author": ""}
        try:
            d = literal_eval(raw_data.decode('utf-8'))
        except:
            print("raw_data Error")
        author = token["author"]
        data = {
            "title": d.get("title"),
            "content": d.get("content"),
            "status": "draft",
            "author": int(author)
        }

        if d.get("postType"): data["type"] = d["postType"]
        auth = (token["user"], token["pass"])
        r = requests.post(url, data=data, auth=auth)
        res = "Post Error"
        if r.json(): res = json.dumps(r.json())

        return res

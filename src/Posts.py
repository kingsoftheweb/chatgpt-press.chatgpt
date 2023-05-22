import json

import quart
import requests
from quart import request
from ast import literal_eval
from dateutil.parser import parse

from src.helpers import indigest, valid_post_type


class Posts:
    """
    Posts class

    This class is used to handle all the requests related to posts.
    Currently, supports:
        - Listing posts 'get_posts()'
        - Adding new posts 'add_new_post()'
        - Update an existing post 'update()'
        - Deleting an existing post 'delete()'
    """

    async def get_post_details(self, token):
        token = indigest(token)
        if token.get("error"): return token
        postType = request.args.get('postType')
        postType = valid_post_type(postType)
        if (request.args.get('postId')):
            url = token["site"] + "/wp-json/wp/v2/" + postType + "/" +request.args.get('postId')
            r = requests.get(url)
            return json.dumps(r.json())

    # TODO Add support for other post types (example 'recipe' post type)
    async def get_posts(self, token):
        token = indigest(token)
        if token.get("error"): return token
        postType = request.args.get('postType')
        postType = valid_post_type(postType)
        url = token["site"] + "/wp-json/wp/v2/"+ postType
        #if request.args.get('postType'): url = token["site"] + '/wp-json/wp/v2/' + request.args.get('postType') + "?"
        url += "?_fields=id,date,link&per_page=10"
        after = request.args.get('afterDate')
        if after: url += "&after=" + parse(after).isoformat()
        before = request.args.get('beforeDate')
        if before: url += "&before=" + parse(before).isoformat()
        r = requests.get(url)
        print(r.json())
        return json.dumps(r.json())

    async def add_new(self, token):
        token = indigest(token)
        postType = request.args.get('postType')
        postType = valid_post_type(postType)
        url = token["site"] + "/wp-json/wp/v2/"+postType
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

        auth = (token["user"], token["pass"])
        r = requests.post(url, data=data, auth=auth)
        res = "Post Error"
        if r.json(): res = json.dumps(r.json())

        return res

    async def update(self, token):
        token = indigest(token)
        postType = request.args.get('postType')
        postType = valid_post_type(postType)
        url = token["site"] + "/wp-json/wp/v2/" + postType +"/"+request.args.get('post_id')
        data = {}
        if(request.args.get('title')):data["title"]=request.args.get('title')
        if(request.args.get('content')):data["content"]=request.args.get('content')
        if(request.args.get('status')):data["status"]=request.args.get('status')
        r = requests.post(url, data=data, auth=(token["user"], token["pass"]))

        return json.dumps(r.json())

    async def delete(self, token, postId):
        token = indigest(token)
        postType = request.args.get('postType')
        postType = valid_post_type(postType)
        url = token["site"] + "/wp-json/wp/v2/" + postType +"/"+postId
        r = requests.delete(url, auth=(token["user"], token["pass"]))

        return json.dumps(r.json())

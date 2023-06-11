import json

import requests
from quart import request
from ast import literal_eval
from dateutil.parser import parse

from src.helpers import validate_site, valid_post_type


class Posts:
    """
    Posts class

    This class is used to handle all the requests related to posts.
    Currently, supports:
        - Listing posts 'get_posts()'
        - Get post details 'get_post_details()'
    """

    async def get_post_details(self):
        site = validate_site(request.args.get('site'))
        if(site.get("error")): return json.dumps(site)
        postType = request.args.get('postType')
        postType = valid_post_type(postType)
        if request.args.get('postId'):
            url = site["site"] + "/wp-json/wp/v2/" + postType + "/" + request.args.get('postId')
            r = requests.get(url)
            return json.dumps(r.json())

    async def get_posts(self):
        site = validate_site(request.args.get('site'))
        if(site.get("error")): return json.dumps(site)
        postType = request.args.get('postType') or request.args.get('type')
        postType = valid_post_type(postType)
        url = site["site"] + "/wp-json/wp/v2/" + postType
        # if request.args.get('postType'): url = token["site"] + '/wp-json/wp/v2/' + request.args.get('postType') + "?"
        url += "?_fields=id,date,link&per_page=10"
        after = request.args.get('afterDate')
        if after: url += "&after=" + parse(after).isoformat()
        before = request.args.get('beforeDate')
        if before: url += "&before=" + parse(before).isoformat()
        r = requests.get(url)
        return json.dumps(r.json())
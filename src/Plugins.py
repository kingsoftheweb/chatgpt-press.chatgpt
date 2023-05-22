import json

import requests

from src.helpers import indigest, plugin_info

class Plugins:
    """
    Plugins class

    This handles all functions related to plugins
    Currently, supports:
        - finding plugins 'find()'
        - install plugins 'install()'
    """

    async def find(self, token, keyword):
        token = indigest(token)
        url = token["site"] + "/wp-json/chatgptpress/v1/plugins/search"
        r = requests.post(url, json={"keyword": keyword}, auth=(token["user"], token["pass"]))
        pList = r.json()
        resList = []
        counter = 0
        info = plugin_info()
        for p in pList:
            if(not info["activate_plugins"].get(p["slug"])):
                counter += 1
                p.pop("short_description")
                resList.append(p)
                if (counter >= 50): break
        res = {
            "action": "chatGPT will find and suggest best plugin to install as user's expectation and compare among them and suggest if compatible with wordpress version",
            "plugins": resList,
            "wordpress_version":info["wordpress_version"]
            }

        return res

    async def install(self, token, slug):
        token = indigest(token)
        url = token["site"] + "/wp-json/chatgptpress/v1/plugins/install"
        r = requests.post(url, json={"slug": slug}, auth=(token["user"], token["pass"]))
        res = r.json()

        return json.dumps(res)

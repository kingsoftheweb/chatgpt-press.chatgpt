import json

import requests

from src.helpers import indigest


class Debug:
    """
    Debug class

    This handles all functions related to debugging the site
    Currently, supports:
        - listing erros and warnings in debug.log 'list()'
    """
    def list(self, token):
        token = indigest(token)
        url = token["site"] + "/wp-json/chatgptpress/v1/debuglog/debug"
        r = requests.get(url, auth=(token["user"], token["pass"]))
        pList = r.json()
        resList = []
        counter = 0
        for p in pList:
            counter += 1
            p.pop("date")
            p.pop("time")
            p.pop("timeZone")
            resList.append(p)
            if counter >= 50: break
        res = {"action": "chatGPT will suggest how to fix this errors", "plugins": resList}

        return json.dumps(res)
import requests

from src.helpers import indigest
class Plugins:
    """
    Plugins class

    This handles all functions related to plugins
    Currently, supports:
        - finding plugins 'find_plugin()'
        - install plugins 'install_plugin()'
    """

    def find_plugin(self, token, keyword):
        token = indigest(token)
        url = token["site"] + "/wp-json/chatgptpress/v1/plugins/search"
        r = requests.post(url, json={"keyword": keyword}, auth=(token["user"], token["pass"]))
        pList = r.json()
        resList = []
        counter = 0
        for p in pList:
            counter += 1
            p.pop("short_description")
            resList.append(p)
            if (counter >= 50): break
        res = {
            "action": "chatGPT will find and suggest best plugin to install as user's expectation and comapre among them and",
            "plugins": resList}

        return res
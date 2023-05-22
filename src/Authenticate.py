import uuid
import datetime
import jwt
import requests
from quart import request

from globals import _SECRET, _CONF, _REDIRECT_TO

from src.helpers import no_site_exception, indigest, login_error_exception


class Authenticate:
    """
    Authenticate class

    This handles all functions related to authentication.
    Currently, supports:
        - starting the authentication process 'start()'
    """

    def start(self, site=False):
        """
        This function will start the authentication process, by calling the /authenticate-chatgptpress endpoint in the
        WordPress site.

        :param site:
        :return:
        """
        if not site: return no_site_exception()
        uid = str(uuid.uuid1())
        try:
            r = requests.get(site)
            if r.status_code != 200:  return {"error": "Please check your web address. It seems invalid."}
        except:
            return {"error": "Please check your web address. It seems invalid."}

        if requests.get(site + "/authenticate-chatgptpress").status_code == 200:
            login_url = site + "/authenticate-chatgptpress?redirect_to=" + _REDIRECT_TO + uid
            _CONF[uid] = {"status": True, "site": site}
            sid = jwt.encode({"uid": uid, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=10)}, _SECRET,
                             algorithm="HS256")
            res = {
                "uid": sid,
                "action": "You need to login manually. chatGPT will show login link: " + login_url
            }
        else:
            res = {"error": "chatgptpress plugin not found in your website. please install the plugin and come back "
                            "again."}

        return res

    def get_token(self):
        try:
            uid = indigest(request.args.get('uid'))["uid"]
        except:
            return {"error": "login link expired", "action": "Get a new login link from /login"}
        inConf = _CONF.get(uid)
        if not inConf: return {"error": "login link expired", "action": "Get a new login link from /login"}
        status = inConf.get("status")
        token = inConf.get("token")
        if status and not token: return self.start()
        if status and token: return {"token": inConf["token"]}
        if not status: return {"error": "Not registed yet"}
        return self.start()

    async def login_to_wordpress(self, uid):
        url = "/wp-json/wp/v2/users/me"
        if not _CONF.get(uid): return "Bad or illegal Request"
        try:
            auth = (request.args.get("username"), request.args.get("appPassword"))
            r = requests.post(_CONF.get(uid)["site"] + url, auth=auth).json()
            if r["id"]: status = "Login successfull, please go back to GPT conversation."
            print(r["id"])
            json_payload = {
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=3),
                "site": _CONF.get(uid)["site"],
                "user": request.args.get("username"),
                "pass": request.args.get("appPassword"),
                "uid": uid,
                "author": str(r["id"])
            }
            _CONF[uid]["token"] = jwt.encode(json_payload, _SECRET, algorithm="HS256")
        except:
            print("error login")
            return """
                <script>
                    alert("Something is wrong!!! Please try again later...");
                    window.close();
                </script>
            """
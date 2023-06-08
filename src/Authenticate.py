import uuid
import datetime
import jwt
import requests
from quart import request

from globals import _SECRET, _CONF

from src.helpers import no_site_exception, indigest


class Authenticate:
    """
    Authenticate class

    This handles all functions related to authentication.
    Currently, supports:
        - starting the authentication process 'start()'
    """

    def start(self, site=None):
        """
        This function will start the authentication process, by calling the /wp-admin/authorize-application.php endpoint in the
        WordPress site.

        :param site:
        :return:
        """
        if not site:
            return no_site_exception()
        uid = str(uuid.uuid1())

        try:
            r = requests.get(site)
            if r.status_code != 200:
                return {
                    "error": "Please check your Web Address. It seems invalid."
                }
        except:
            return {
                "error": "Please check your Web Address. It seems invalid."
            }
        # We should put the / before wp-admin/ (when it does not exist) because the site variable
        # is coming without a ending /
        if site[-1] == "/":
            authentication_url = site + "wp-admin/authorize-application.php"
        else:
            authentication_url = site + "/wp-admin/authorize-application.php"

        if requests.get(authentication_url).status_code == 200:
            current_timestamp = datetime.datetime.now().timestamp()
            app_name = "ChatGPTPress" + str(current_timestamp)
            login_url = authentication_url + "?app_name=" + app_name
            _CONF[uid] = {
                "status": True,
                "site": site
            }
            sid = jwt.encode(
                {
                    "uid": uid,
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
                }, _SECRET, algorithm="HS256")

            res = {
                "uid": sid,
                "action": "You need to authenticate manually over the WordPress site."
                          + "ChatGPT will show the Authorization link: " + login_url + " to the user."
                          + "After login provide your username and password so ChatGPT will proceed."
            }
        else:
            res = {
                "error": "Authorization is not active on your site. Please make sure to activate it."
                         + "Here is a helpful link: "
                         + "https://make.wordpress.org/core/2020/11/05/application-passwords-integration-guide/#Getting-Credentials"
            }

        return res

    def get_token(self):
        uid = None
        try:
            uid = indigest(request.args.get('uid'))["uid"]
        except:
            return {"error": "login link expired", "action": "Get a new login link from /login"}
        inConf = _CONF.get(uid)
        if not inConf: return {"error": "login link expired", "action": "Get a new login link from /login"}
        status = inConf.get("status")
        token = inConf.get("token")
        # HERE SHOULD BE REQUESTED WITH USER AND PASS
        # if status and not token: return self.start()
        auth = (request.args.get("username"), request.args.get("appPassword"))
        if status and not token and uid: return self.login_to_wordpress(uid, auth)
        if status and token: return {"token": inConf["token"]}
        if not status: return {"error": "Not registed yet"}
        # HERE SHOULD BE REQUESTED WITH USER AND PASS
        return self.start()

    # THIS FUNCTION SHOULD BE USED AS DEPENDENT
    def login_to_wordpress(self, uid, auth):
        url = "/wp-json/wp/v2/users/me"
        if not _CONF.get(uid): return "Bad or illegal Request"
        try:
            r = requests.post(_CONF.get(uid)["site"] + url, auth=auth).json()
            json_payload = {
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=3),
                "site": _CONF.get(uid)["site"],
                "user": request.args.get("username"),
                "pass": request.args.get("appPassword"),
                "uid": uid,
                "author": str(r["id"])
            }
            _CONF[uid]["token"] = jwt.encode(json_payload, _SECRET, algorithm="HS256")
            return {
                "token": _CONF[uid]["token"]
            }
        except:
            return {
                "Error": "Error to login the wp site. please try again later"
            }

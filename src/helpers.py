import requests

def validate_site(site_url):
    # return a valid https url
    if site_url.startswith("http://"):
        site_url = site_url.replace("http://", "https://")
    
    if not site_url.startswith("https://"):
        site_url = "https://" + site_url
    
    try:
        r = requests.get(site_url)
        if r.status_code != 200:
            return {
                "error": "Please check your Web Address. It seems invalid wordpress website."
            }
    except:
        return {
            "error": "Please check your Web Address. It seems invalid."
        }
    return {"site":site_url,"error":False}


def valid_post_type(postType):
    if postType == "post" or postType is None:
        return "posts"
    return postType

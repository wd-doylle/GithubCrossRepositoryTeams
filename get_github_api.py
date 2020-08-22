import requests
import logging
import time
import json


def get_github_api(url,auth_token,headers=None):

    for i in range(5):
        try:
            if headers:
                r = requests.get(url,auth=tuple(auth_token),headers=headers)
            else:
                r = requests.get(url,auth=tuple(auth_token))
            if not 'X-RateLimit-Remaining' in r.headers:
                logging.critical(r.content)
            else:
                break
        except Exception as e:
            logging.critical(e)
            if i == 4:
                return None
            time.sleep(10)
    if int(r.headers['X-RateLimit-Remaining']) <= 2:
        logging.critical("RATE LIMIT EXCEEDED ON ACCOUNT:%s!"%(auth_token[0]))
        while time.time() < int(r.headers['X-RateLimit-Reset']):
            time.sleep(300)
        return get_github_api(url,auth_token,headers)
    if not r.content:
        j = []
    else:
        j = json.loads(r.content.decode('utf-8'))
    if 'message' in j:
        logging.critical(j['message']+'\turl:'+url)
        return None
    return j
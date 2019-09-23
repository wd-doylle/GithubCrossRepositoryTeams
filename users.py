import json
import sys



with open('users.json','w') as uj:
    user_logins = set()
    with open('contributors.json') as cj:
        for line in cj.readlines():
            j = json.loads(line)
            for u in j['contributors']:
                if u['login'] in user_logins:
                    continue
                user = {
                    'id':u['id'],
                    'login':u['login'],
                }
                json.dump(user,uj)
                uj.write('\n')
                user_logins.add(u['login'])
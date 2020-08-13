import requests
import urllib3
import gzip
import json
import os
import re

try:
    cbp = open('build_dataset.bp')
    tasks = json.load(cbp)
except:
    cbp = open('build_dataset.bp','w')
    tasks = {'year':2015,'month':1, 'day':1}
    json.dump(tasks,cbp)
finally:
    cbp.close()

year = tasks['year']
month = tasks['month']
day = tasks['day']
print(year,month,day)

root_dir = 'issuecomment'
if not os.path.exists(root_dir):
    os.mkdir(root_dir)

# s = requests.Session()
for y in [2015,2016,2017,2018,2019,2020]:
    if y<year:
        continue
    year_dir = os.path.join(root_dir,str(y))
    if not os.path.exists(year_dir):
        os.mkdir(year_dir)
    for m in range(1,13):
        if m<month:
            continue
        month_dir = os.path.join(year_dir,'%d-%02d'%(y,m))
        if not os.path.exists(month_dir):
            os.mkdir(month_dir)
        for d in range(1,32):
            if d<day:
                continue
            out_path = os.path.join(month_dir,"%d-%02d-%02d.json.gz"%(y,m,d))
            with gzip.open(out_path,'wt') as f:
                for h in range(24):
                    r = requests.get("https://data.gharchive.org/%d-%02d-%02d-%d.json.gz"%(y,m,d,h))
                    if not r.ok:
                        break
                    try:
                        lines = gzip.decompress(r.content)
                        lines = lines.split(b'\n')
                    except MemoryError:
                        with open("%d-%02d-%02d-%d.json.gz"%(y,m,d,h),'wb') as gz:
                            gz.write(r.content)
                        continue
                    for l in lines[:-1]:
                        l = l.decode('utf-8')
                        j = json.loads(l)
                        if j['type'] == 'IssueCommentEvent':
                            try:
                                save = {
                                    'repo_name':j['repo']['name'],
                                    'actor_login':j['actor']['login'],
                                    'created_at':j['created_at'],
                                    'issue_id':j['payload']['issue']['id'],
                                    'body':j['payload']['comment']['body']
                                }
                            except:
                                continue
                            json.dump(save,f)
                            f.write('\n')
                    print(y,m,d,h)
            day = d+1
            with open('build_dataset.bp','w') as bp:
                json.dump({'year':year,'month':month,'day':day},bp)
        month = m+1
        day = 1
    year = y+1
    month = 1


for file in os.listdir('.'):
    res = re.match("([0-9]{4})-([0-9]{2})-([0-9]{2})-([0-9]{1,2}).json.gz",file)
    if res:
        y,m,d,h = [int(i) for i in res.groups()]
        with gzip.open(file,'rt') as gz:
            out_path = os.path.join(root_dir,str(y),'%d-%02d'%(y,m),"%d-%02d-%02d.json.gz"%(y,m,d))
            with gzip.open(out_path,'at') as f:
                for line in gz.readlines():
                    j = json.loads(line)
                    if j['type'] == 'IssueCommentEvent':
                        try:
                            save = {
                                'repo_name':j['repo']['name'],
                                'actor_login':j['actor']['login'],
                                'created_at':j['created_at'],
                                'issue_id':j['payload']['issue']['id'],
                                'body':j['payload']['comment']['body']
                            }
                        except:
                            continue
                        json.dump(save,f)
                        f.write('\n')
        print(y,m,d,h)
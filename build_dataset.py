import requests
import urllib3
import gzip
import json
import os

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

s = requests.Session()
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
        for d in range(1,31):
            if d<day:
                continue
            out_path = os.path.join(month_dir,"%d-%02d-%02d.json"%(y,m,d))
            with open(out_path,'w') as f:
                for h in range(24):
                    r = s.get("https://data.gharchive.org/%d-%02d-%02d-%d.json.gz"%(y,m,d,h))
                    if not r.ok:
                        break
                    lines = gzip.decompress(r.content).decode('utf-8').split('\n')[:-1]
                    del r
                    for l in lines:
                        j = json.loads(l)
                        if j['type'] == 'IssueCommentEvent':
                            save = {
                                'repo_name':j['repo']['name'],
                                'actor_login':j['actor']['login'],
                                'created_at':j['created_at'],
                                'issue_id':j['payload']['issue']['id'],
                                'body':j['payload']['comment']['body']
                            }
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

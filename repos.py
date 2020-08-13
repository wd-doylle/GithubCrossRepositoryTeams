import json
import os
import gzip

root_dir = 'issuecomment'


repos = set()
with open('repos.txt','w') as rp:
    for y in [2015,2016,2017,2018,2019,2020]:
        year_dir = os.path.join(root_dir,str(y))
        for m in range(1,13):
            month_dir = os.path.join(year_dir,'%d-%02d'%(y,m))
            for d in range(1,32):
                file_path = os.path.join(month_dir,"%d-%02d-%02d.json.gz"%(y,m,d))
                if not os.path.exists(file_path):
                    continue
                with gzip.open(file_path,'rt') as f:
                    for line in f.readlines():
                        j = json.loads(line)
                        repo = j['repo_name']
                        if not repo in repos:
                            repos.add(repo)
                            rp.write(repo+'\n')
            print(y,m,d)



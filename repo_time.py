import json
import sys
import os
import gzip

repos_filename = sys.argv[1]
output_filename = sys.argv[2]


repos = set()
with open('repos.txt') as rj:
    for i,repo in enumerate(rj.readlines()):
        repo = repo.strip()
        repos.add(repo)
    print(len(repos))

root_dir = "issuecomment/"

print("Computing PR Comments...")
repo_time = {}
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
                        time = j['created_at']
                        if time == 'None' or not time:
                            continue
                        if repo in repos:
                            if not repo in repo_time:
                                repo_time[repo] = [time,time]
                            else:
                                if time < repo_time[repo][0]:
                                    repo_time[repo][0] = time
                                elif time > repo_time[repo][1]:
                                    repo_time[repo][1] = time
                print(y,m,d)

print("Outputting...")
with open(output_filename,'w') as of:
    for repo in repo_time:
        of.write('%s\t%s\t%s\n'%(repo,repo_time[repo][0],repo_time[repo][1]))
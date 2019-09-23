import json
import sys
import os

repos_filename = sys.argv[1]
output_filename = sys.argv[2]

bp = [0,0,0]

repos = set()

print("Reading repos...")
with open(repos_filename) as rf:
    rj = json.load(rf)
    for repo in rj:
        repos.add(repo['full_name'])

issue_comment_dir = "../GithubGroupDetection/issuecomment/"

print("Computing PR Comments...")
year = bp[0]
month = bp[1]
day = bp[2]
years = os.listdir(issue_comment_dir)
months = os.listdir(issue_comment_dir+years[year])
days = os.listdir(issue_comment_dir+years[year]+'/'+months[month])


repo_time = {}

for y in range(year,len(years)):
    months = os.listdir(issue_comment_dir+years[y])
    for m in range(month,len(months)):
        days = os.listdir(issue_comment_dir+years[y]+'/'+months[m])
        for d in range(day,len(days)):
            with open(issue_comment_dir+years[y]+'/'+months[m]+'/'+days[d]) as ic:
                for line in ic.readlines():
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
                    if not repo:
                        break
            print(y,m,d)
            if not repo:
                break
        day = 0
        if not repo:
            break
    month = 0
    if not repo:
        break

print("Outputting...")
with open(output_filename,'w') as of:
    for repo in repo_time:
        of.write('%s\t%s\t%s\n'%(repo,repo_time[repo][0],repo_time[repo][1]))
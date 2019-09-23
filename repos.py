import json
import os

year = 0
month = 0
day = 0

years = os.listdir('issuecomment')
months = os.listdir('issuecomment/'+years[year])
days = os.listdir('issuecomment/'+years[year]+'/'+months[month])
repos = set()
repo_detials = []
for y in range(year,len(years)):
    months = os.listdir('issuecomment/'+years[y])
    for m in range(month,len(months)):
        days = os.listdir('issuecomment/'+years[y]+'/'+months[m])
        for d in range(day,len(days)):
            with open('issuecomment/'+years[y]+'/'+months[m]+'/'+days[d]) as ic:
                for line in ic.readlines():
                    j = json.loads(line)
                    repo = {
                        'id':j['repo_id'],
                        'full_name':j['repo_name']
                    }
                    if not repo['full_name'] in repos:
                        repos.add(repo['full_name'])
                        repo_detials.append(repo)
            print(y,m,d)



with open('repos.json','w') as rp:
    json.dump(repo_detials,rp)
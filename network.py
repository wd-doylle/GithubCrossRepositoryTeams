import json
import sys
import os
import gzip


network_filename = sys.argv[1]
time_filename = sys.argv[2]

nodes = []
aware = []
duration = []

user_logins = set()
with open("users.json") as uj:
    for u in uj.readlines():
        j = json.loads(u)
        user_logins.add(j['login'])

node_indicies = {}

print("Computing PR Comments...")
years = os.listdir('issuecomment')
months = os.listdir('issuecomment/'+years[0])
days = os.listdir('issuecomment/'+years[0]+'/'+months[0])
issue_partis = {}
for y in range(len(years)):
    months = os.listdir('issuecomment/'+years[y])
    for m in range(len(months)):
        days = os.listdir('issuecomment/'+years[y]+'/'+months[m])
        for d in range(len(days)):
            with gzip.open('issuecomment/'+years[y]+'/'+months[m]+'/'+days[d],'rt') as ic:
                for line in ic.readlines():
                    j = json.loads(line)
                    if not 'body' in j or not j['body']:
                        continue
                    if not j['actor_login'] in user_logins:
                        continue
                    if not j['issue_id'] in issue_partis:
                        issue_partis[j['issue_id']] = [j['actor_login']]
                    else:
                        issue_partis[j['issue_id']].append(j['actor_login'])
                    atter = j['actor_login']
                    repo = j['repo_name']
                    time = j['created_at']
                    for word in j['body'].split():
                        if word[0] == "@":
                            attee = word[1:]
                            if attee in issue_partis[j['issue_id']]:
                                continue
                            if not attee in user_logins:
                                continue
                            try:
                                u1 = node_indicies[atter]
                            except:
                                nodes.append(atter)
                                u1 = len(nodes) - 1
                                aware.append({})
                                duration.append({})
                                node_indicies[atter] = u1
                            try:
                                u2 = node_indicies[attee]
                            except:
                                nodes.append(attee)
                                u2 = len(nodes) - 1
                                aware.append({})
                                duration.append({})
                                node_indicies[attee] = u2
                            u1,u2 = min(u1,u2),max(u1,u2)
                            if u2 in aware[u1]:
                                if not repo in aware[u1][u2]:
                                    aware[u1][u2].append(repo)
                            else:
                                aware[u1][u2] = [repo,]
                            if u2 in duration[u1]:
                                duration[u1][u2][0] = min(time,duration[u1][u2][0])
                                duration[u1][u2][1] = max(time,duration[u1][u2][1])
                            else:
                                duration[u1][u2] = [time,time]
            print(y,m,d)

print("Outputting...")
network = {
    'nodes':nodes,
    'aware':aware,
}
with open(network_filename,'w') as nj:
    json.dump(network,nj)
with open(time_filename,'w') as ol:
    for i in range(len(duration)):
        for j in duration[i]:
            ol.write("%s\t%s\t%s\t%s\n"%(nodes[i],nodes[int(j)],duration[i][j][0],duration[i][j][1]))
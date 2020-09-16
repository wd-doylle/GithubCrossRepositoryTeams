import json
import sys

network_filename = sys.argv[1]
output_filename = sys.argv[2]
output_filename_single = sys.argv[3]

print("Reading Aware......")

try:
    with open(network_filename) as nf:
        j = json.load(nf)
        nodes = j['nodes']
        aware = j['aware']
except:
    print("No network nodes!")
    exit(1)

contrs = []
contr_repos = []
for i in range(len(nodes)):
    contrs.append([[],[]])
    contr_repos.append([])
    

node_indices = {}
for i in range(len(nodes)):
    node_indices[nodes[i]] = i

print("Computing contribution...")
with open('contributors.json') as cj:
    repo = ""
    repo_ind = -1
    contributors = []
    contributions = []
    for line in cj.readlines():
        js = json.loads(line)
        if repo != js['repo']:
            contributors.sort()
            for i in range(len(contributors)):
                for j in range(i+1,len(contributors)):
                    if not str(contributors[j]) in aware[contributors[i]]:
                        continue
                    try:
                        ind = contrs[contributors[i]][0].index(contributors[j])
                        contrs[contributors[i]][1][ind] += min(contributions[i],contributions[j])
                        contr_repos[contributors[i]][ind] += (repo,)
                    except:
                        contrs[contributors[i]][0].append(contributors[j])
                        contrs[contributors[i]][1].append(min(contributions[i],contributions[j]))
                        contr_repos[contributors[i]].append((repo,))
            repo = js['repo']
            repo_ind += 1
            contributors = []
            contributions = []
            if repo_ind % 10000 == 0:
                print(repo_ind)
        for u in js['contributors']:
            try:
                contributors.append(node_indices[u['login']])
                contributions.append(u['contributions'])
            except KeyError:
                continue         



print("Outputting......")
with open(output_filename,'w') as od:
    with open(output_filename.rpartition('.')[0]+'.link','w') as ol:
        with open(output_filename_single,'w') as ods:
            with open(output_filename_single.rpartition('.')[0]+'.link','w') as ols:
                for i in range(len(contrs)):
                    for j in range(len(contrs[i][0])):
                        if len(contr_repos[i][j]) > 0:
                            ods.write('%d\t%d\t%f\n'%(i,contrs[i][0][j],1))
                            ols.write('%s\t%s\t%s\n'%(nodes[i],nodes[contrs[i][0][j]],json.dumps(contr_repos[i][j])))
                        repos = set()
                        for r in contr_repos[i][j]:
                            repos.add(r.split('/')[-1])
                        if len(repos) > 1:
                            od.write('%d\t%d\t%f\n'%(i,contrs[i][0][j],1))
                            ol.write('%s\t%s\t%s\n'%(nodes[i],nodes[contrs[i][0][j]],json.dumps(contr_repos[i][j])))

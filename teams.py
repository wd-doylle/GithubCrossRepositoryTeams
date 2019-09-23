import sys
import json


file_tp = sys.argv[1]
file_network = sys.argv[2]
file_out = sys.argv[3]


print("Reading nodes...")
nodes = []
with open(file_network) as lb:
    j = json.load(lb)
    nodes = j['nodes']



print("Reading Modules...")
teams = []
with open(file_tp) as tp:
    size = 0
    for line in tp.readlines():
        if line[0] == "#":
            words = line.split()
            size = int(words[3])
            if size <= 1:
                break
        else:
            words = line.split()
            teams.append([nodes[int(w)] for w in words])



print("Outputting...")
with open(file_out,'w') as tms:
    for team in teams:
        tms.write(json.dumps(team))
        tms.write('\n')
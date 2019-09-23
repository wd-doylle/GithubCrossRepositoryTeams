import sys
import json
import random
import time

file_edges = sys.argv[1]
file_tp = sys.argv[2]
file_pajek_orig = sys.argv[3]
file_network = sys.argv[4]

random.seed(time.time())

print("Reading Labels...")
user_logins = []
with open(file_network) as lb:
    j = json.loads(lb.read())
    user_logins = j['nodes']


print("Reading Modules...")
vers = set()
teams = []
size_ind = []
with open(file_tp) as tp:
    size = 0
    for line in tp.readlines():
        if line[0] == "#":
            words = line.split()
            size = int(words[3])
            if size <= 1:
                break
        else:
            if size==2:
                continue
            
            words = line.split()
            teams.append([int(w) for w in words])
            size_ind.append(size)
top_ind = sorted(list(range(len(size_ind))),key=lambda x:size_ind[x],reverse=True)
for i in range(100):
    vers.update(teams[top_ind[i]])



print("Reading Colors...")
colors = []
with open("pajek_colors.txt") as pjc:
    colors = pjc.read().split()


vertices = []
arcs = []
indices = {}
vertices_without_singleton = []
arcs_without_singleton = []
indices_without_singleton = {}
flag = 0
print("Reading Original Pajek...")
with open(file_pajek_orig) as pj_orig:
    repainting = {}
    for line in pj_orig.readlines():
        if line.startswith("*Vertices"):
            continue
        elif line.startswith("*Edges"):
            flag = 1
        elif line.startswith("*Arcs"):
            flag = 2
        elif flag == 0:
            words = line.split()
            ver = int(words[1].strip('"'))
            words[1] = '"%s"' % (user_logins[ver])
            if words[-1] in repainting:
                words[-1] = repainting[words[-1]]
            else:
                color_ind = random.randrange(0,len(colors))
                repainting[words[-1]] = colors[color_ind]
                words[-1] = colors[color_ind]
                # colors.pop(color_ind)
            vertices.append(words[1:])
            indices[ver]=len(vertices)-1
            if ver in vers:
                vertices_without_singleton.append(words[1:])
                indices_without_singleton[ver]=len(vertices_without_singleton)-1
        else:
            break


print("Reading Network...")
arcs = []
with open(file_edges) as osl:
    for line in osl.readlines():
        words = line.split()
        ver1 = int(words[0])
        ver2 = int(words[1])
        arcs.append([ver1,ver2,float(words[2])])
        if ver1 in vers and ver2 in vers:
            arcs_without_singleton.append([ver1,ver2,float(words[2])])


print("Outputting...")
with open(file_pajek_orig.rpartition(".")[0]+"_new.net",'w') as pj_new:
    pj_new.write("*Vertices %d\n" % (len(vertices)))
    for ind,ver in enumerate(vertices):
        pj_new.write("  %d %s\n" % (ind+1," ".join(ver)))
    if flag == 1:
        pj_new.write("*Edges\n")
    elif flag == 2:
        pj_new.write("*Arcs\n")
    else:
        print("UNEXPECTED ERROR!")
        exit(1)
    for arc in arcs:
        pj_new.write("%d %d %f\n"%(indices[arc[0]]+1,indices[arc[1]]+1,arc[2]))
with open(file_pajek_orig.rpartition(".")[0]+"_new_without_singleton.net",'w') as pj_new_without_sing:
    pj_new_without_sing.write("*Vertices %d\n" % (len(vertices_without_singleton)))
    for ind,ver in enumerate(vertices_without_singleton):
        pj_new_without_sing.write("  %d %s\n" % (ind+1," ".join(ver)))
    if flag == 1:
        pj_new_without_sing.write("*Edges\n")
    elif flag == 2:
        pj_new_without_sing.write("*Arcs\n")
    for arc in arcs_without_singleton:
        pj_new_without_sing.write("%d %d %f\n"%(indices_without_singleton[arc[0]]+1,indices_without_singleton[arc[1]]+1,arc[2]))

import json
import sys
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats  
from datetime import datetime


repo_feature_stat_filename = sys.argv[1]


blue = "#3333FF"
save_dir = 'c:\\Users\\doylle\\Desktop\\'

print("Computing statistics...")
reposize_teams = {}
repowatchers_teams = {}
repoforks_teams = {}
reposubscribers_teams = {}
reposize_contr_rate = {}
repowatchers_contr_rate = {}
repoforks_contr_rate = {}
reposubscribers_contr_rate = {}
cntr_test_A = []
team_cnt_test_A = []
cntr_test_B = []
with open(repo_feature_stat_filename) as tmj:
    cntr_test_A = json.loads(tmj.readline())
    team_cnt_test_A = json.loads(tmj.readline())
    cntr_test_B = json.loads(tmj.readline())


minimal_team_cnt = 10

def plot_chunked(values,x_l,x_r,x_label,y_label,value_cnt):
    bins = 50
    chunked = [0]*bins
    x_r = x_r + 1
    step_size = (x_r-x_l)/bins
    chunk_value_cnt = [0]*bins
    for s in values.keys():
        if int(s) > x_r:
            continue
        chunk_value_cnt[int((int(s)-x_l)//step_size)] += value_cnt[s]
    for s in values:
        if int(s) > x_r:
            continue
        chunked[int((int(s)-x_l)//step_size)] += values[s]/chunk_value_cnt[int((int(s)-x_l)//step_size)]
    fig, ax = plt.subplots()
    ax.bar([x_l+i*step_size for i in range(bins)],chunked,width=step_size,color=blue)
    ax.set_xlim(left=x_l,right=x_r)
    ax.set_xticks([x_l+i*((x_r-x_l)/5) for i in range(6)])
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    fig.savefig(save_dir+y_label.replace(' ','_')+" _v_"+x_label.replace(' ','_')+".pdf",bbox_inches='tight')

print("Plotting...")


# sizes = [int(s) for s in reposize_teams.keys()]
# plot_chunked(reposize_teams,min(sizes),max(sizes),"Repository Size","Average # of Teams",dict.fromkeys(reposize_teams,1))

# watchers = [int(s) for s in repowatchers_teams.keys()]
# plot_chunked(repowatchers_teams,min(watchers),max(watchers),"Repository Watchers","Average # of Teams",dict.fromkeys(repowatchers_teams,1))

# forks = [int(s) for s in repoforks_teams.keys()]
# plot_chunked(repoforks_teams,min(forks),max(forks),"Repository Forks","Average # of Teams",dict.fromkeys(repoforks_teams,1))

# subscribers = [int(s) for s in reposubscribers_teams.keys()]
# plot_chunked(reposubscribers_teams,min(subscribers),max(subscribers),"Repository Subscribers","Average # of Teams",dict.fromkeys(reposubscribers_teams,1))

# sizes = [int(s) for s in reposize_contr_rate.keys()]
# plot_chunked(reposize_contr_rate,min(sizes),max(sizes),"Repository Size","Average Contribution Ratio",reposize_teams)

# watchers = [int(s) for s in repowatchers_contr_rate.keys()]
# plot_chunked(repowatchers_contr_rate,min(watchers),max(watchers),"Repository Watchers","Average Contribution Ratio",repowatchers_teams)

# forks = [int(s) for s in repoforks_contr_rate.keys()]
# plot_chunked(repoforks_contr_rate,min(forks),max(forks),"Repository Forks","Average Contribution Ratio",repoforks_teams)

# subscribers = [int(s) for s in reposubscribers_contr_rate.keys()]
# plot_chunked(reposubscribers_contr_rate,min(subscribers),max(subscribers),"Repository Subscribers","Average Contribution Ratio",reposubscribers_teams)

cntr_test_A = np.array(cntr_test_A,copy=True)
cntrs = np.asarray(cntr_test_A[:,-1],dtype=np.float32)
sizes = np.asarray(cntr_test_A[:,0],dtype=np.int32)
forks = np.asarray(cntr_test_A[:,1],dtype=np.int32)
contributors = np.asarray(cntr_test_A[:,2],dtype=np.int32)
start_times = np.array([datetime.strptime(t, '%Y-%m-%dT%H:%M:%SZ').timestamp() for t in cntr_test_A[:,3]])

r,p = stats.pearsonr(sizes,cntrs)
print(r,p)
r,p = stats.pearsonr(forks,cntrs)
print(r,p)
r,p = stats.pearsonr(contributors,cntrs)
print(r,p)
r,p = stats.pearsonr(start_times,cntrs)
print(r,p)
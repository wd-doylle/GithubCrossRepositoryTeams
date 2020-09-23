import json
import sys
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import heapq
from matplotlib import rcParams

repo_stat_filename = sys.argv[1]
# repo_language_filename = sys.argv[2]
# repo_topic_filename = sys.argv[3]

blue = "#3333FF"

rcParams['axes.labelsize'] = 18
rcParams['ytick.labelsize'] = 18
rcParams['xtick.labelsize'] = 18
rcParams['axes.titlesize'] = 18

print("Computing statistics...")
repos = []
repo_contrs = []
repo_contrs_by_teams = []
repo_contrs_by_single_teams = []
repo_sizes = []
repo_ratio_of_teams = []
repo_ratio_of_single_teams = []
repo_team_cnts = []
with open(repo_stat_filename) as tmj:
    for tml in tmj.readlines():
        repo,cnt_t,contr,contr_t,size,size_t,contr_t_s,size_t_s = tml.split('\t')
        repos.append(repo)
        repo_team_cnts.append(int(cnt_t))
        repo_contrs.append(int(contr))
        repo_sizes.append(int(size))
        repo_contrs_by_teams.append(json.loads(contr_t))
        repo_contrs_by_single_teams.append(json.loads(contr_t_s))
        repo_ratio_of_teams.append(json.loads(size_t))
        repo_ratio_of_single_teams.append(json.loads(size_t_s))


# language_cnt = {}
# with open(repo_language_filename) as ff:
#     repo,lang = ff.split()
#     lang = json.loads(lang)
#     for lan in lang:
#         if not lan in language_cnt:
#             language_cnt[lan] = 0
#         language_cnt[lan] += lang[lan]

# topic_cnt = {}
# with open(repo_topic_filename) as ff:
#     repo,topic = ff.split()
#     topic = json.loads(topic)
#     for top in topic:
#         if not top in language_cnt:
#             language_cnt[top] = 0
#         topic_cnt[top] += topic[top]


# repo_topics = sorted(topic_cnt.items(),key=lambda x:x[1],reverse=True)
# repo_languages = sorted(language_cnt.items(),key=lambda x:x[1],reverse=True)

# repo_cnt = 10
# sorted_indices = sorted(range(len(repos)),key=lambda x: repo_contrs[x],reverse=True)
# display_indices = [sorted_indices[int(len(repos)/repo_cnt*i)] for i in range(repo_cnt)]
display_indices = [repos.index(r) for r in ["twbs/bootstrap","vuejs/vue","facebook/react","d3/d3","nodejs/node","flutter/flutter","angular/angular.js","docker/docker","angular/angular","golang/go"]]
repo_cnt = len(display_indices)

print("Plotting...")
fig, ax = plt.subplots()
ax.hist(repo_team_cnts,range=(0,30),bins=30,color=blue)
ax.set_xlim(left=1)
ax.set_xticks(list(range(1,31)))
ax.set_xlabel("#Teams in Repos")
ax.set_ylabel("Count")


fig, ax = plt.subplots()
par1 = ax.twinx()
bar_width = 0.4
r_cons = [(repo_contrs[i]-repo_contrs_by_teams[i]-repo_contrs_by_single_teams[i])for i in display_indices]
t_cons = [repo_contrs_by_teams[i] for i in display_indices]
t_s_cons = [repo_contrs_by_single_teams[i] for i in display_indices]
b_cons = [(repo_contrs[i]-repo_contrs_by_teams[i])for i in display_indices]

r_siz = [repo_sizes[i]-repo_ratio_of_teams[i]-repo_ratio_of_single_teams[i] for i in display_indices]
t_siz = [repo_ratio_of_teams[i] for i in display_indices]
t_s_siz = [repo_ratio_of_single_teams[i]*1.5 for i in display_indices]
b_siz = [repo_sizes[i]-repo_ratio_of_teams[i] for i in display_indices]

bar1 = ax.bar(range(repo_cnt),r_cons,bar_width,color="#3333FF",label='contribution',edgecolor='black')
br1 = ax.bar(range(repo_cnt),t_s_cons,bar_width,bottom=r_cons,color="#4444FF",edgecolor='black')
b1 = ax.bar(range(repo_cnt),t_cons,bar_width,bottom=b_cons,color="#6699FF",edgecolor='black')


bar2 = par1.bar([ind+bar_width for ind in range(repo_cnt)],r_siz,bar_width,color="#FF3333",label='contributors',edgecolor='black')
br2 = par1.bar([ind+bar_width for ind in range(repo_cnt)],t_s_siz,bar_width,bottom=r_siz,color="#FF6666",edgecolor='black')
b2 = par1.bar([ind+bar_width for ind in range(repo_cnt)],t_siz,bar_width,bottom=b_siz,color="#FF9999",edgecolor='black')
ax.set_xticklabels([repos[i] for i in display_indices])
# ax.set_yticklabels(list(range(0,60001,10000)))
ax.set_xticks([i+bar_width/2 for i in range(repo_cnt)])
ax.set_ylabel("Contributions",color='b')
ax.tick_params(axis='y', colors='b')
# ax.set_ylim(0,120000)
par1.set_yticklabels(list(range(0,601,100)))
par1.set_ylabel("Contributors",color='r')
par1.tick_params(axis='y', colors='r')
par1.set_ylim(0,600)
fig.autofmt_xdate()
ax.legend([bar1,br1,b1,bar2,br2,b2], ["Contribution of Individuals","Contribution of Regular Teams","Contribution of ISCTs","Individual Contributors","Members of Regular Teams","Members of ISCTs"],ncol=2,fontsize=14)

for i in range(repo_cnt):
    ax.text(i, r_cons[i]+t_cons[i]/2+t_s_cons[i]-7,"%.2f"%(t_cons[i]/(t_cons[i]+t_s_cons[i]+r_cons[i])), ha='center', va='bottom',fontsize=14)
    ax.text(i, r_cons[i]+t_s_cons[i]/2-7,"%.2f"%(t_s_cons[i]/(t_cons[i]+t_s_cons[i]+r_cons[i])), ha='center', va='center',fontsize=14)
    par1.text(i+bar_width, r_siz[i]+t_siz[i]/2+t_s_siz[i]-7,"%.2f"%(t_siz[i]/(t_siz[i]+t_s_siz[i]+r_siz[i])), ha='center', va='bottom',fontsize=14)
    par1.text(i+bar_width, r_siz[i]+t_s_siz[i]/2-7,"%.2f"%(t_s_siz[i]/(t_siz[i]+t_s_siz[i]+r_siz[i])), ha='center', va='center',fontsize=14)


# fig.savefig(save_dir+'TeamContributionRepos.pdf')
plt.show()
import json
import sys
import datetime
import networkx as nx
import numpy as np
import scipy

link_filename = sys.argv[1]
team_filename = sys.argv[2]
link_single_filename = sys.argv[3]
team_single_filename = sys.argv[4]
topic_filename = sys.argv[5]
language_filename = sys.argv[6]
feature_filename = sys.argv[7]
time_filename = sys.argv[8]
contribution_filename = sys.argv[9]
repo_time_filename = sys.argv[10]
output_filename = sys.argv[11]


print("Loading Links...")
links = {}
with open(link_filename) as lkj:
	for line in lkj.readlines():
		dep,ter,repos = line.split('\t')
		if dep in links:
			links[dep][ter] = json.loads(repos)
		else:
			links[dep] = {ter:json.loads(repos)}

links_single = {}
with open(link_single_filename) as lkj:
	for line in lkj.readlines():
		dep,ter,repos = line.split('\t')
		if dep in links_single:
			links_single[dep][ter] = json.loads(repos)
		else:
			links_single[dep] = {ter:json.loads(repos)}

print("Loading Topics...")
repo_topics = {}
topic_repos = {}
with open(topic_filename) as tf:
	for line in tf.readlines():
		repo,labels = line.split('\t')
		labels = json.loads(labels)
		for t in labels:
			if not t in topic_repos:
				topic_repos[t] = 0
			topic_repos[t] += 1
		repo_topics[repo] = labels

print("Loading Languages...")
repo_languages = {}
lang_repos = {}
with open(language_filename) as lf:
	for line in lf.readlines():
		repo,langs = line.split('\t')
		langs = sorted(json.loads(langs).items(),key=lambda x:x[1],reverse=True)[:2]
		langs = [l[0] for l in langs]
		for t in langs:
			if not t in lang_repos:
				lang_repos[t] = 0
			lang_repos[t] += 1
		repo_languages[repo] = langs

print("Loading repo features...")
repo_features = {}
repo_feature_total = []
feature_repo_cnt = [{},{},{},{}]
repo_team_cnt = {}
with open(feature_filename) as ff:
	for line in ff.readlines():
		repo,feats = line.split('\t')
		repo_features[repo] = json.loads(feats)
		repo_features[repo] = [repo_features[repo]['size'],repo_features[repo]['watchers'],repo_features[repo]['forks'],repo_features[repo]['subscribers_count']]
		if not repo_features[repo][0] in feature_repo_cnt[0]:
			feature_repo_cnt[0][repo_features[repo][0]] = 0
		feature_repo_cnt[0][repo_features[repo][0]] += 1
		if not repo_features[repo][1] in feature_repo_cnt[1]:
			feature_repo_cnt[1][repo_features[repo][1]] = 0
		feature_repo_cnt[1][repo_features[repo][1]] += 1
		if not repo_features[repo][2] in feature_repo_cnt[2]:
			feature_repo_cnt[2][repo_features[repo][2]] = 0
		feature_repo_cnt[2][repo_features[repo][2]] += 1
		if not repo_features[repo][3] in feature_repo_cnt[3]:
			feature_repo_cnt[3][repo_features[repo][3]] = 0
		feature_repo_cnt[3][repo_features[repo][3]] += 1
		repo_feature_total.append(repo_features[repo])
		repo_team_cnt[repo] = 0
repo_feature_total = np.array(repo_feature_total)
VI = np.linalg.inv(np.cov(repo_feature_total.T))
print(VI)
VAR = repo_feature_total.var(0)
print(VAR)
DIS = 0
MEAN = repo_feature_total.mean(0)
print(MEAN)
for rf in repo_feature_total:
	DIS += scipy.spatial.distance.mahalanobis(rf,MEAN,VI)/len(repo_feature_total)
print(DIS)


print("Loading repo time...")
repo_time = {}
with open(repo_time_filename) as tf:
	for line in tf.readlines():
		repo,start,end = line.strip().split('\t')
		repo_time[repo] = (start,end)


print("Loading contribution...")
repo_ind = {}
contributions = []
total_contrs = []
with open(contribution_filename) as cf:
	i = 0
	for line in cf.readlines():
		j = json.loads(line)
		repo_ind[j['repo']] = i
		contrs = {}
		contions = []
		total_contr = 0
		for cntr in j['contributors']:
			contrs[cntr['login']] = cntr['contributions']
			total_contr += cntr['contributions']
		contributions.append(contrs)
		total_contrs.append(total_contr)
		i += 1

print("Computing Labels & Contributions...")
teams = []
team_repos = []
team_topics = []
team_languages = []
contr_rates = []
repo_team_members = {}
team_language_diff = []
team_topic_diff = []
team_reposize_var = []
team_repowatchers_var = []
team_repoforks_var = []
team_reposubscribers_var = []
team_repofeature_dis = []
contr_test_A = []
team_cnt_test_A = []
team_member_test_A = []
with open(team_filename) as tmj:
	for tml in tmj.readlines():
		tm = json.loads(tml)
		topics = {}
		languages = {}
		contrs = {}
		size = {}
		watchers = {}
		forks = {}
		subscribers = {}
		contr_rate = {}
		for member in tm:
			if not member in links:
				continue
			for ter in links[member]:
				if ter in tm:
					for repo in links[member][ter]:
						if repo not in repo_ind:
							continue
						if not repo in contrs:
							contrs[repo] = set()
						if member in contributions[repo_ind[repo]]:
							contrs[repo].add(member)
						if ter in contributions[repo_ind[repo]]:
							contrs[repo].add(ter)
						if repo in repo_topics:
							topics[repo] = repo_topics[repo]
						else:
							topics[repo] = []
						if repo in repo_languages:
							languages[repo] = repo_languages[repo]
						if repo in repo_features:
							size[repo] = repo_features[repo][0]
							watchers[repo] = repo_features[repo][1]
							forks[repo] = repo_features[repo][2]
							subscribers[repo] = repo_features[repo][3]
		repos = {}
		for repo in watchers:
			name = repo.split('/')[-1]
			if not name in repos or watchers[repo]>watchers[repos[name]]:
				repos[name] = repo
		repos = repos.values()
		if len(repos) < 2:
			continue
		contrs_new = {}
		topics_new = {}
		languages_new = {}
		size_new = {}
		watchers_new = {}
		forks_new = {}
		subscribers_new = {}
		for repo in repos:
			contrs_new[repo] = contrs[repo]
			topics_new[repo] = topics[repo]
			if repo in languages:
				languages_new[repo] = languages[repo]
			size_new[repo] = size[repo]
			watchers_new[repo] = watchers[repo]
			forks_new[repo] = forks[repo]
			subscribers_new[repo] = subscribers[repo]
		contrs = contrs_new
		topics = topics_new
		languages = languages_new
		size = size_new
		watchers = watchers_new
		forks = forks_new
		subscribers = subscribers_new
		contribution = 0
		total_contribution = 0
		for repo in contrs:
			_contribution = 0
			for mem in contrs[repo]:
				_contribution += contributions[repo_ind[repo]][mem]/len(contrs[repo])
			total_contribution += total_contrs[repo_ind[repo]]/len(contributions[repo_ind[repo]])
			contr_rate[repo] = _contribution/(total_contrs[repo_ind[repo]]/len(contributions[repo_ind[repo]]))
			contribution += _contribution
			if not repo in repo_team_members:
				repo_team_members[repo] = set()
			repo_team_members[repo].update(contrs[repo])
			repo_team_cnt[repo] += 1
		topic_sim = 0
		topics = [set(t) for t in list(topics.values())]
		tps = set()
		lang_sim = 0
		languages = [set(l) for l in list(languages.values())]
		langs = set()
		for i in range(len(topics)):
			tps.update(topics[i])
			for j in range(i+1,len(topics)):
				topic_sim += 1-len(topics[i].intersection(topics[j]))/len(topics[i].union(topics[j])) if topics[i] or topics[j] else 0
		for i in range(len(languages)):
			langs.update(languages[i])
			for j in range(i+1,len(languages)):
				lang_sim += 1-len(languages[i].intersection(languages[j]))/len(languages[i].union(languages[j]))
		if len(topics)>1:
			topic_sim /= len(topics)*(len(topics)-1)/2
		else:
			topic_sim = -1
		if len(languages)>1:
			lang_sim /= len(languages)*(len(languages)-1)/2
		else:
			lang_sim = -1
		for repo in repos:
			if not repo in repo_time or not repo in repo_languages:
				continue
			if not repo in repo_topics:
				topic_rs = [0]
			else:
				topic_rs = [topic_repos[t] for t in repo_topics[repo]]
			lang_rs = [lang_repos[t] for t in repo_languages[repo]]
			contr_test_A.append([size[repo],forks[repo],len(contributions[repo_ind[repo]]),repo_time[repo],max(topic_rs),max(lang_rs),np.mean(topic_rs),np.mean(lang_rs),contr_rate[repo]])
		size = list(size.values())
		watchers = list(watchers.values())
		forks = list(forks.values())
		subscribers = list(subscribers.values())
		feature_mean = np.mean([repo_features[r] for r in repos],0)
		teams.append(tm)
		team_repos.append(repos)
		contr_rate['all'] = contribution/total_contribution
		contr_rates.append(contr_rate)
		team_language_diff.append(lang_sim)
		team_topic_diff.append(topic_sim)
		team_topics.append(list(tps))
		team_languages.append(list(langs))
		team_reposize_var.append(np.var(size)/VAR[0])
		team_repowatchers_var.append(np.var(watchers)/VAR[1])
		team_repoforks_var.append(np.var(forks)/VAR[2])
		team_reposubscribers_var.append(np.var(subscribers)/VAR[3])
		team_repofeature_dis.append(np.mean([scipy.spatial.distance.mahalanobis(repo_features[r],feature_mean,VI) for r in repos])/DIS)
for repo in repo_team_cnt:
	if not repo in repo_time or not repo in repo_languages or not repo in repo_ind:
		continue
	if not repo in repo_topics:
		topic_rs = [0]
	else:
		topic_rs = [topic_repos[t] for t in repo_topics[repo]]
	lang_rs = [lang_repos[t] for t in repo_languages[repo]]
	team_cnt_test_A.append([repo_features[repo][0],repo_features[repo][2],len(contributions[repo_ind[repo]]),repo_time[repo],max(topic_rs),max(lang_rs),np.mean(topic_rs),np.mean(lang_rs),repo_team_cnt[repo]])
for repo in repo_team_members:
	if not repo in repo_time or not repo in repo_languages:
		continue
	if not repo in repo_topics:
		topic_rs = [0]
	else:
		topic_rs = [topic_repos[t] for t in repo_topics[repo]]
	lang_rs = [lang_repos[t] for t in repo_languages[repo]]
	team_member_test_A.append([repo_features[repo][0],repo_features[repo][2],len(contributions[repo_ind[repo]]),repo_time[repo],max(topic_rs),max(lang_rs),np.mean(topic_rs),np.mean(lang_rs),len(repo_team_members[repo])])

repo_team_single_members = {}
repo_team_cnt_single = {}
contr_test_B = []
with open(team_single_filename) as tmj:
	for tml in tmj.readlines():
		tm = json.loads(tml)
		repos = set()
		for member in tm:
			if not member in links_single:
				continue
			for ter in links_single[member]:
				if ter in tm:
					for repo in links_single[member][ter]:
						if repo not in repo_ind:
							continue
						repos.add(repo)
		contrs = {}
		for repo in repos:
			for mem in tm:
				if mem not in contributions[repo_ind[repo]]:
					continue
				if not repo in contrs:
					contrs[repo] = []
				contrs[repo].append(mem)
				if not repo in repo_team_single_members:
					repo_team_single_members[repo] = set()
				repo_team_single_members[repo].update(contrs[repo])
		for repo in contrs:
			_contribution = 0
			for mem in contrs[repo]:
				_contribution += contributions[repo_ind[repo]][mem]/len(contrs[repo])
			contr_rate = _contribution/(total_contrs[repo_ind[repo]]/len(contributions[repo_ind[repo]]))
			if not repo in repo_team_cnt_single:
				repo_team_cnt_single[repo] = 0
			repo_team_cnt_single[repo] += 1
			if not repo in repo_features or not repo in repo_time or not repo in repo_languages:
				continue
			if not repo in repo_topics:
				topic_rs = [0]
			else:
				topic_rs = [topic_repos[t] for t in repo_topics[repo]]
			lang_rs = [lang_repos[t] for t in repo_languages[repo]]
			contr_test_B.append([repo_features[repo][0],repo_features[repo][2],len(contributions[repo_ind[repo]]),repo_time[repo],max(topic_rs),max(lang_rs),np.mean(topic_rs),np.mean(lang_rs),contr_rate])
print("Computing Center...")
team_centers = []
team_aspls = []
team_acs = []
team_cens = []
team_sizes = []
for i in range(len(teams)):
	tm = teams[i]
	repos = team_repos[i]
	G = nx.Graph()
	# G.add_nodes_from(tm)
	G_r = {}
	# degrees = {}
	for member in tm:
		if not member in links:
			continue
		for ter in links[member]:
			if ter in tm:
				if not member in G or not ter in G[member]:
					G.add_edge(member,ter)
				for repo in links[member][ter]:
					if not repo in repos:
						continue
					if not repo in G_r:
						G_r[repo] = nx.Graph()
					if not member in G_r[repo] or not ter in G_r[repo][member]:
						G_r[repo].add_edge(member,ter)
	centers = {}
	aspls = {}
	acs = {}
	cens = {}
	sizes = {}
	for repo in G_r:
		if not nx.is_connected(G_r[repo]):
			continue
		degree_cen = nx.degree_centrality(G_r[repo]).items()
		degree_cen = sorted(degree_cen, key=lambda x:x[1])
		nodes = [d_c[0] for d_c in degree_cen]
		cns = [d_c[1] for d_c in degree_cen]
		centers[repo] = nodes[cns.index(cns[-1]):]
		aspls[repo] = nx.average_shortest_path_length(G_r[repo])
		acs[repo] = nx.average_clustering(G_r[repo])
		degree_cen = nx.degree_centrality(G_r[repo])
		cens[repo] = (max(cns)*len(G_r[repo])-sum(cns))/(len(G_r[repo])-2) if len(G_r[repo])>2 else 0
		sizes[repo] = len(G_r[repo].nodes)
	if not nx.is_connected(G):
		print(tm)
		# continue
	degree_cen = nx.degree_centrality(G).items()
	degree_cen = sorted(degree_cen, key=lambda x:x[1])
	nodes = [d_c[0] for d_c in degree_cen]
	cns = [d_c[1] for d_c in degree_cen]
	centers['all'] = nodes[cns.index(cns[-1]):]
	aspls['all'] = nx.average_shortest_path_length(G) if nx.is_connected(G) else -1
	acs['all'] = nx.transitivity(G) if nx.is_connected(G) else -1
	cens['all'] = (cns[-1]*len(G)-sum(cns))/(len(G)-2) if len(G)>2 else 0
	team_centers.append(centers)
	team_acs.append(acs)
	team_aspls.append(aspls)
	team_cens.append(cens)
	team_sizes.append(sizes)
	# print(len(team_cens))

print("Computing Existing Duration...")
network_time = {}
with open(time_filename) as tf:
	for line in tf.readlines():
		m1,m2,t1,t2 = line.strip().split('\t')
		if m1 in network_time:
			network_time[m1][m2] = [t1,t2]
		else:
			network_time[m1] = {m2:[t1,t2]}

team_durations = []
for tm in teams:
	start = None
	end = None
	for m1 in tm:
		if not m1 in network_time:
			continue
		for m2 in network_time[m1]:
			if m2 in tm:
				time1 = datetime.datetime.strptime(network_time[m1][m2][0], '%Y-%m-%dT%H:%M:%SZ')
				time2 = datetime.datetime.strptime(network_time[m1][m2][1], '%Y-%m-%dT%H:%M:%SZ')
				if not start or start>time1:
					start = time1
				if not end or end<time2:
					end = time2
	team_durations.append((end-start).days+1)
	
team_reposize = []
for repos in team_repos:
	repo_size = {}
	for repo in repos:
		repo_size[repo] = len(contributions[repo_ind[repo]])
	team_reposize.append(repo_size)

print("Computing Repo Statistics...")
repo_contrs_by_teams = []
repo_ratio_of_teams = []
repo_contrs_by_single_teams = []
repo_ratio_of_single_teams = []
for repo in repo_team_members:
	contr_t = 0
	contr_t_s = 0
	cnt = 0
	for mem in repo_team_members[repo]:
		contr_t += contributions[repo_ind[repo]][mem]
	if repo in repo_team_single_members:
		for mem in repo_team_single_members[repo]:
			if not mem in repo_team_members[repo]:
				contr_t_s += contributions[repo_ind[repo]][mem]
				cnt += 1
	repo_contrs_by_teams.append(contr_t)
	repo_ratio_of_teams.append(len(repo_team_members[repo]))
	repo_contrs_by_single_teams.append(contr_t_s)
	repo_ratio_of_single_teams.append(cnt)



print(len(teams),len(team_topics),len(team_topic_diff))

print("Outputting...")
with open(output_filename,'w') as lj:
	for i in range(len(teams)):
		if team_aspls[i]['all']<0:
			continue
		json.dump(teams[i],lj)
		lj.write('\t')
		lj.write('%d\t'%team_durations[i])
		json.dump(team_topics[i],lj)
		lj.write('\t')
		json.dump(team_languages[i],lj)
		lj.write('\t')
		json.dump(contr_rates[i],lj)
		lj.write('\t')
		json.dump(team_centers[i],lj)
		lj.write('\t')
		json.dump(team_aspls[i],lj)
		lj.write('\t')
		json.dump(team_acs[i],lj)
		lj.write('\t')
		json.dump(team_cens[i],lj)
		lj.write('\t')
		json.dump(team_sizes[i],lj)
		lj.write('\t')
		json.dump(team_reposize[i],lj)
		lj.write('\t%f\t%f\t%f\t%f\t%f\t%f\t%f\n'%(team_language_diff[i],team_topic_diff[i],team_reposize_var[i],team_repowatchers_var[i],team_repoforks_var[i],team_reposubscribers_var[i]
									,team_repofeature_dis[i]))


with open(output_filename.rpartition('/')[0]+"/repo_statistics.txt",'w') as rj:
	i = 0
	for repo in repo_team_members:
		rj.write("%s\t%d\t%d\t"%(repo,repo_team_cnt[repo],total_contrs[repo_ind[repo]]))
		json.dump(repo_contrs_by_teams[i],rj)
		rj.write('\t%d\t'%len(contributions[repo_ind[repo]]))
		json.dump(repo_ratio_of_teams[i],rj)
		rj.write('\t')
		json.dump(repo_contrs_by_single_teams[i],rj)
		rj.write('\t')
		json.dump(repo_ratio_of_single_teams[i],rj)
		rj.write('\n')
		i += 1


with open(output_filename.rpartition('/')[0]+"/repo_feature_statistics.txt",'w') as rj:
	rj.write('%s\n'%json.dumps(contr_test_A))
	rj.write('%s\n'%json.dumps(team_cnt_test_A))
	rj.write('%s\n'%json.dumps(team_member_test_A))
	rj.write('%s\n'%json.dumps(contr_test_B))
	# rj.write('%s\n'%json.dumps(team_cnt_test_B))
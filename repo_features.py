import json
import requests
import time
import threading
import queue
import logging

try:
    cbp = open('repo_features.bp')
    tasks = json.load(cbp)
except:
    cbp = open('repo_features.bp','w')
    tasks = []
    json.dump(tasks,cbp)
finally:
    cbp.close()


index = 0
repos = []
with open('contributors.json') as rj:
    ind = 0
    for line in rj.readlines():
        j = json.loads(line)
        repo = j['repo']
        repos.append(repo)
        if repo in tasks:
            index = ind
        ind += 1
print(len(repos))
print(index)

auth_tokens = [
    """
    Github personal access tokens (Must belong to different accounts)
    """
]

with open('github_tokens.cred') as cj:
    auth_tokens = json.load(cj)

headers = {
    "Accept":"application/vnd.github.mercy-preview+json"
}


logging.basicConfig(filename='repo_features.log',level=logging.WARNING,
format='%(asctime)s %(filename)s %(levelname)s %(threadName)s %(message)s')


def request(url,auth_account):
    
    for i in range(5):
        try:
            r = requests.get(url,auth=auth_account,headers=headers)
            break
        except Exception as e:
            logging.critical(e)
            if i == 4:
                return []
            time.sleep(10)
    if not r.content:
        return []
    j = json.loads(r.content.decode('utf-8'))
    if int(r.headers['X-RateLimit-Remaining']) <= proc_cnt:
        logging.critical("RATE LIMIT EXCEEDED ON ACCOUNT:%s!"%(auth_account[0]))
        while time.time() < int(r.headers['X-RateLimit-Reset']):
            time.sleep(300)
    if 'message' in j:
        logging.warning(j['message']+'\turl:'+url)
        return []
    return j

def saving(repo,features,tasks):
    with open('repo_features.json','a') as cj:
        cj.write(repo+'\t')
        json.dump(features,cj)
        cj.write('\n')
    tasks.remove(repo)
    with open('repo_features.bp','w') as cbp:
        json.dump(tasks,cbp)


def main(repo,auth_account,proc_cnt):

    j = request('https://api.github.com/repos/'+repo,auth_account)
    if not j:
        return {}
    features = {
        'size':j['size'],
        'watchers':j['watchers'],
        'forks':j['forks'],
        'subscribers_count':j['subscribers_count'],
    }
    # j = request('https://api.github.com/repos/'+repo+'languages',auth_account)
    # features['languages'] = j
    # j = request('https://api.github.com/repos/'+repo+'topics',auth_account)
    # features['topics'] = j['names'] if j else []
    return features




def consumer(task_queue,tasks,result_queue,auth_account,proc_cnt):

    while True:
        next_task = task_queue.get()
        if next_task is None:
           # Poison pill means shutdown
            logging.warning('Exiting')
            task_queue.task_done()
            break
        repo = next_task
        logging.warning(next_task)
        features = main(repo,auth_account,proc_cnt)
        task_queue.task_done() # Must be called the same times as .get()
        result_queue.put([repo,features])


def producer(repos,ind,task_queue,tasks,proc_cnt):

    for i in range(ind,len(repos)):
        repo = repos[i]
        task_queue.put(repo)
        tasks.append(repo)
    for i in range(proc_cnt):
        task_queue.put(None)

task_queue = queue.Queue(maxsize=10)
result_queue = queue.Queue(maxsize=10)
proc_cnt = len(auth_accounts)*2

threads = []
for i in range(proc_cnt):
    t = threading.Thread(target=consumer,name="Thread#"+str(i+1),args=(task_queue,tasks,result_queue,auth_accounts[i//2],2),daemon=True)
    threads.append(t)
    t.start()

for t in tasks:
    task_queue.put(t)
t = threading.Thread(target=producer,args=(repos,index+1,task_queue,tasks,proc_cnt),daemon=True)
t.start()

while True:
    try:
        repo,features = result_queue.get(timeout=60)
    except:
        break
    saving(repo,features,tasks)
    result_queue.task_done()

logging.critical("Done")

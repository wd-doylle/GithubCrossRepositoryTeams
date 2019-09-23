import json
import requests
import time
import threading
import queue
import logging

try:
    cbp = open('repo_topics.bp')
    tasks = json.load(cbp)
except:
    cbp = open('repo_topics.bp','w')
    tasks = []
    json.dump(tasks,cbp)
finally:
    cbp.close()


index = -1
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

auth_accounts = [
    """
    Github accounts for authentication
    Format:
        (username,password)
    """
]

logging.basicConfig(filename='repo_topics.log',level=logging.WARNING,
format='%(asctime)s %(filename)s %(levelname)s %(threadName)s %(message)s')


def saving(repo,topics,tasks):
    with open('repo_topics.json','a') as cj:
        cj.write(repo+'\t')
        json.dump(topics,cj)
        cj.write('\n')
    tasks.remove(repo)
    with open('repo_topics.bp','w') as cbp:
        json.dump(tasks,cbp)


def main(repo,auth_account,proc_cnt):

    for i in range(5):
        try:
            r = requests.get('https://api.github.com/repos/'+repo+"/topics",auth=auth_account)
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
        logging.critical("RATE LIMIT EXCEEDED ON ACCOUNT:%s!"%(auth_account))
        while time.time() < int(r.headers['X-RateLimit-Reset']):
            time.sleep(300)
    if 'message' in j:
        logging.warning(j['message']+'\turl:https://api.github.com/repos/'+repo+"/topics")
        return []
    return j



def consumer(task_queue,tasks,result_queue,auth_account,proc_name,proc_cnt):

    while True:
        next_task = task_queue.get()
        if next_task is None:
           # Poison pill means shutdown
            logging.warning('Exiting')
            task_queue.task_done()
            break
        repo = next_task
        logging.warning(next_task)
        topics = main(repo,auth_account,proc_cnt)
        task_queue.task_done() # Must be called the same times as .get()
        result_queue.put([repo,topics])


def producer(repos,ind,task_queue,tasks,proc_cnt):

    for i in range(ind,len(repos)):
        repo = repos[i]
        task_queue.put(repo)
        tasks.append(repo)
    for i in range(proc_cnt):
        task_queue.put(None)

task_queue = queue.Queue(maxsize=10)
result_queue = queue.Queue(maxsize=10)
proc_cnt = len(auth_accounts)

threads = []
for i in range(proc_cnt):
    t = threading.Thread(target=consumer,name="Thread#"+str(i+1),args=(task_queue,tasks,result_queue,auth_accounts[i],"Thread#"+str(i+1),proc_cnt),daemon=True)
    threads.append(t)
    t.start()

for t in tasks:
    task_queue.put(t)
t = threading.Thread(target=producer,args=(repos,index+1,task_queue,tasks,proc_cnt),daemon=True)
t.start()

while True:
    try:
        repo,topics = result_queue.get(timeout=60)
    except:
        break
    saving(repo,topics,tasks)
    result_queue.task_done()

print("Done")

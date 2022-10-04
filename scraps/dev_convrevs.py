import json
import os
import time

def ensure_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

now=time.strftime('%Y%m%d%H%M%S',time.localtime())
# Get most recent counts for each product.
tables={}
with open('tables.json','r') as f:
    tables=json.loads(f.read())
ensure_dir("data/backup/tables")
with open("data/backup/tables/"+now+".json","w+") as g:
    g.write(json.dumps(tables,indent=2))

for t in tables:
    if not 'polist' in tables[t]:
        continue
    for p in tables[t]['polist']:
        if not 'rev' in tables[t]['polist'][p]:
            continue
        # print(tables[t]['polist'][p])
        revs=tables[t]['polist'][p]['rev']
        if not isinstance(tables[t]['polist'][p]['rev'],dict):
            tables[t]['polist'][p]['rev']={}
        for r in revs:
            if not r in tables[t]['polist'][p]['rev']:
                tables[t]['polist'][p]['rev'][r]={}
            if not 'times' in tables[t]['polist'][p]['rev'][r]:
                tables[t]['polist'][p]['rev'][r]['times']=tables[t]['polist'][p]['times']
        # print(tables[t]['polist'][p])
with open('tables.json','w+') as g:
    g.write(json.dumps(tables,indent=2))

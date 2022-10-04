#!/usr/bin/python3
import csv
import json
import time
from datetime import datetime
from time import mktime
import os
def ensure_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

nowt=datetime.fromtimestamp(mktime(time.localtime()))
nowstr=time.strftime('%Y%m%d%H%M%S',time.localtime())
tbj=open('tables.json','r')
tables=json.loads(tbj.read())
ensure_dir("data/backup/tables")
with open("data/backup/tables"+nowstr+".json","w+") as g:
    g.write(json.dumps(tables,indent=2))

for t in tables:
    # ttime=datetime.fromtimestamp(mktime(time.strptime(tables[t]['times']['accessed'],'%Y%m%d%H%M%S')))
    # tdelta=nowt-ttime
    if 'polist' in tables[t]:
        for p in tables[t]['polist']:
            if 'bin' in tables[t]['polist'][p]:
                if tables[t]['polist'][p]['bin']!="":
                    print(tables[t]['polist'][p]['bin'])
            # ptime=datetime.fromtimestamp(mktime(time.strptime(tables[t]['polist'][p]['times']['accessed'],'%Y%m%d%H%M%S')))
            # pdelta=nowt-ptime
            # if int(pdelta.days)>0:
            #     print('  '+t+p+': '+str(pdelta.days))
    # print(json.dumps(tables,indent=2))

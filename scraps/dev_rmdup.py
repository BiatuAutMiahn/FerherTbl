import json

totals=None
with open('data/counts/totals_2.json','r') as f:
    totals=json.loads(f.read())
for d in ['20190614','20190612','20190612','20190611','20190610','20190607','20190606']:
    for p in totals[d]:
        if 'counts' in totals[d][p]:
            counts=list(dict.fromkeys(totals[d][p]['counts']))
            totals[d][p]['counts']=counts
        if 'ovf' in totals[d][p]:
            for b in totals[d][p]['ovf']:
                counts=list(dict.fromkeys(totals[d][p]['ovf'][b]))
                totals[d][p]['ovf'][b]=counts

with open("data/counts/totals_2.json","w+") as g:
    g.write(json.dumps(totals,indent=2))

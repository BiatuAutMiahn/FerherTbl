
import os.path
import json
from collections import OrderedDict

countpg=49

tables=None
if os.path.isfile('tables.json'):
    with open('tables.json') as f:
        tables=json.loads(f.read())
#
# class DictSubSortLen(OrderedDict):
#     def __init__(self, **kwargs):
#         super(DictSubSortLen, self).__init__()
#         for key, value in sorted(kwargs.items(), key=lambda x: len(x[1]), reverse=True):
#             if isinstance(value, dict):
#                 self[key] = DictSubSortLen(**value)
#             else:
#                 self[key] = value
#
# def keyfunc(tup):
#     key, d = tup
#     print(d)
#     return d["downloads"], d["date"]
#
# items = sorted(tables.items(), key = keyfunc)

# tables=DictSubSortLen(**tables)
# tables=OrderedDict(sorted(tables.items(), key=lambda t: len(t[0])))

for t in tables:
    if not 'polist' in tables[t]:
        print(t)
        for s in tables[t]:
            if s in ['times','type']:
                continue
            print(' '+s+','+str(len(tables[t][s]['polist'])))
    else:
        if t in ['times','type']:
            continue
        print(t+','+str(len(tables[t]['polist'])))

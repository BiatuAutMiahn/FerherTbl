import json
import pandas as pd

temp = pd.read_excel(open("meta/Counts FG SideBolsters  D  F 06.24.2019.xlsx", 'rb'),sheet_name='Master D & F')
pulls=['550225122300480','550225122400480','550225122300461','550225122400461','550225116102485','550225116202485','550225116102400','550225116202400','550225116102478','550225116202478']
print(temp)
newz=[]
for i,row in temp.iterrows():
    prod=row['Customer Material Number']
    mat=row['Material']
    if len(prod)!=12:
        continue
    print(mat)
    if prod in newz:
        continue
    if mat in pulls:
        print('  '+mat)
        newz.append(prod)

newz=sorted(newz, key=lambda x: int(x[-4:]))
newz=sorted(newz, key=lambda x: int(x[0:4]))
newz2=[]
pulls=sorted(pulls, key=lambda x: int(x))
for p in pulls:
    newz2.append(p[0:2]+'.'+p[2:4]+'.'+p[4:6]+'.'+p[6:10]+'-'+p[10:12]+'.'+p[12:15])
    # a=p[0:3]
    # b=p[3:6]
    # c=p[6:9]
    # d=p[9:12]
    # e=p[12:15]
    # if not a in newz2:
    #     newz2[a]={}
    # if not b in newz2[a]:
    #     newz2[a][b]={}
    # if not c in newz2[a][b]:
    #     newz2[a][b][c]={}
    # if not d in newz2[a][b][c]:
    #     newz2[a][b][c][d]=[]
    # if not e in newz2[a][b][c][d]:
    #     newz2[a][b][c][d].append(e)

# print(newz2)
#
# for a in newz2:
#     if len(newz2)>1:
#         print(a)
#     else:
#         print(a,end='')
#     for b in newz2[a]:
#         if len(newz2[a])>1:
#             print('')
#             print("    "+b)
#         else:
#             print(b,end='')
#         for c in newz2[a][b]:
#             if len(newz2[a][b][c])>1:
#                 print('')
#                 print("    "+c)
#             else:
#                 print(c,end='')
#             for d in newz2[a][b][c]:
#                 # if len(newz2[a][b][c])>1:
#                 #     print("    "+d)
#                 # else:
#                 #     print(d,endl='')
#                 # for e in newz2[a][b][c][d]:
#                     if len(newz2[a][b][c][d])==1:
#                         print(d,end='')
#                         print(newz2[a][b][c][d][0])
#                     else:
#                         print("        "+d)
#                         for e in newz2[a][b][c][d]:
#                             print("            "+e)
#             # print("    "+c)
#             # for d in newz2[a][b][c]:

print('')
for p in newz2:
    print(p)

exit()
# temp=[]
# with open("data/counts/totals_2.json") as f:
#     temp=json.loads(f.read())

for d in temp:
    for p in temp[d]:
        if '-' in p:
            continue
        if len(p)!=12:
            continue
        if p in newz:
            continue
        newz.append(p)

for p in newz:
    print(p)

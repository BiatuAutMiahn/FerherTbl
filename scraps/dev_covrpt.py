import pandas as pd
import json
import time
import os


def ensure_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

now=time.strftime('%Y%m%d%H%M%S',time.localtime())
# Get most recent counts for each product.
totals={}
with open('data/counts/totals_2.json','r') as f:
    totals=json.loads(f.read())
tables={}
with open('tables.json','r') as f:
    tables=json.loads(f.read())
ensure_dir("data/backup/tables")
with open("data/backup/tables/"+now+".json","w+") as g:
    g.write(json.dumps(tables,indent=2))

coverage = pd.read_excel(open('meta/coverage/DAILY COVERAGE 6.21.19.xlsx', 'rb'),sheet_name='Sheet1')
print(coverage)

# Perform Import
igntbl=[]
# ignprod=[]
for index, row in coverage.iterrows():
    prod=row['Component']
    desc=row['Object description']
    if len(prod)!=11:
        continue
    a=prod[0:3]
    b=prod[3:7]
    c=prod[8:11]
    if a in igntbl:
        continue
    if not a in tables:
        print('"'+a+'" Not in Tables')
        igntbl.append(a)
        continue
    if not 'polist' in tables[a]:
        continue
    if not b in tables[a]['polist']:
        print('"'+b+'" Not in "'+a+'"')
        # ignprod.append(a)
        continue
    for p in tables[a]['polist']:
        if p!=b:
            continue
        if not 'desc' in tables[a]['polist'][p]:
            tables[a]['polist'][p]['desc']=''
        if 'rev' in tables[a]['polist'][p]:
            if not c in tables[a]['polist'][p]['rev']:
                tables[a]['polist'][p]['rev'].append(c)
                print(prod+', "'+c+'" != "'+str(tables[a]['polist'][p]['rev'])+'"')
        if desc is not None and desc is not '':
            if tables[a]['polist'][p]['desc']!=desc:
                print(prod+', "'+desc+'" != "'+tables[a]['polist'][p]['desc']+'"')
            tables[a]['polist'][p]['desc']=desc
with open('tables.json','w+') as g:
    g.write(json.dumps(tables,indent=2))
exit()
# ncounts={}
# for index, row in coverage.iterrows():
#     prod=row['Component']
#     for d in totals:
#         for p in totals[d]:
#             if not '-' in p:
#                 continue
#             if p==prod:
#                 if not d in ncounts:
#                     ncounts[d]={}
#                 if not p in ncounts[d]:
#                     ncounts[d][p]=0
#                 counts=0
#                 if 'counts' in totals[d][p]:
#                     for c in totals[d][p]['counts']:
#                         if '*' in c:
#                             spl=c.split('*')
#                             counts+=int(spl[0])*int(spl[1])
#                         else:
#                             counts+=int(c)
#                 if 'ovf' in totals[d][p]:
#                     for b in totals[d][p]['ovf']:
#                         for c in totals[d][p]['ovf'][b]:
#                             if '*' in c:
#                                 spl=c.split('*')
#                                 counts+=int(spl[0])*int(spl[1])
#                             else:
#                                 counts+=int(c)
#                 ncounts[d][p]=counts
#                 if p=='1601772-004':
#                     print(str(d)+','+str(p)+','+str(counts))
# # print(json.dumps(ncounts,indent=2))
# # print(list(ncounts.keys()).reversed())
# coverage.at[index,'Comments'].astype(str)
# coverage = coverage.astype({"Comments": str})
# dates=sorted(list(ncounts.keys()))[-4:]
# for d in dates:
#     date=time.strftime('%m/%d',time.strptime(d,'%Y%m%d'))
#     cols = len(coverage.columns.tolist())
#     if not 'Counts '+date in coverage.columns:
#         coverage.insert(cols-1,'Counts '+date,'')
# for index,row in coverage.iterrows():
#     prod=row['Component']
#     coverage.at[index,'Comments']=''
#     # for d in ncounts:
#     for d in dates[::-1]:
#         date=time.strftime('%m/%d',time.strptime(d,'%Y%m%d'))
#         cols = len(coverage.columns.tolist())
#         if not prod in ncounts[d]:
#             continue
#         for p in ncounts[d]:
#             skip=False
#             # print(dates[::-1])
#             # exit()
#             for dc in dates[::-1]:
#                 datec=time.strftime('%m/%d',time.strptime(dc,'%Y%m%d'))
#                 if 'Counts '+datec in coverage.columns:
#                     if coverage.at[index,'Counts '+datec]!='':
#                         skip=True
#             if prod==p:
#                 # print(d)
#                 # print(p)
#                 coverage.at[index,'Counts '+date]=ncounts[d][p]
#                 if skip:
#                     continue
#                 if int(ncounts[d][p])>=int(row['2 day + b/o']):
#                     coverage.at[index,'Comments']='Covered'
#                 else:
#                     coverage.at[index,'Comments']='Backorder'
#
#
# # print(coverage)
# writer = pd.ExcelWriter('export/coverage_test_2019.06.21.xlsx', engine='xlsxwriter')
# df = coverage
# df.to_excel(writer,sheet_name='Coverage 06.21',index=False)
# workbook = writer.book
# #worksheet = workbook.add_worksheet('Cycle Counts')
# worksheet = writer.sheets['Coverage 06.21']
# #worksheet.add_table('A1:'+chr(ord('A')+len(new_tots))+str(len(new_tots['PO'])))
# for idx, col in enumerate(df):  # loop through all columns
#     series = df[col]
#     max_len = max((
#         series.astype(str).map(len).max(),  # len of largest item
#         len(str(series.name))  # len of column name/header
#         )) + 1  # adding a little extra space
#     worksheet.set_column(idx, idx, max_len)  # set column width
# formatShadeRows = workbook.add_format({'border':1,
#                                        'bg_color': '#E3E3E3',
#                                        'font_color': 'black',
#                                        'border_color': 'black'})
# formatBorders = workbook.add_format({'border': 1,
#                                      'border_color': 'black'})
# worksheet.conditional_format('A1:'+chr(ord('A')+df.shape[1]-1)+str(df.shape[0]+1),{'type': 'formula',
#                                                                           'criteria': '=MOD(ROW(),2) = 0',
#                                                                           'format': formatShadeRows})
# worksheet.conditional_format('A1:'+chr(ord('A')+df.shape[1]-1)+str(df.shape[0]+1),{'type': 'no_errors','format': formatBorders})
# worksheet.freeze_panes(1,0)
# shift="2nd"
# stamp=time.strftime('%Y.%m.%d',time.localtime())
# worksheet.set_header("&L"+shift+" Shift Cycle Counts Coverage "+stamp+"&RPage:&P/&N",{'margin':0.3})
# worksheet.fit_to_pages(1,0)
# worksheet.orientation=0
# worksheet.set_margins(left=0.25,right=0.25,top=0.5,bottom=0.0)
# # worksheet.repeat_columns('A:'+chr(ord('A')+df.shape[1]-1))
# writer.save()
#
#
#
#     # print()

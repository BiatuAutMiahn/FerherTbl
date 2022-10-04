import pandas as pd
import json
import time
import os
from collections import OrderedDict
import natsort


def ensure_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

class DictSubSortNat(OrderedDict):
    def __init__(self, **kwargs):
        super(DictSubSortNat, self).__init__()
        for key, value in natsort.natsorted(kwargs.items()):
            if isinstance(value, dict):
                self[key] = DictSubSortNat(**value)
            else:
                self[key] = value

now=time.strftime('%Y%m%d%H%M%S',time.localtime())
# Get most recent counts for each product.
# totals={}
# with open('data/counts/totals_2.json','r') as f:
#     totals=json.loads(f.read())
# tables={}
# with open('tables.json','r') as f:
#     tables=json.loads(f.read())
# ensure_dir("data/backup/tables")
# with open("data/backup/tables/"+now+".json","w+") as g:
#     g.write(json.dumps(tables,indent=2))
meta={}
with open('meta.json','r') as f:
    meta=json.loads(f.read())
# imp = pd.read_excel(open('meta/Bader count sheet.xlsx', 'rb'))
# imp = pd.read_excel(open('meta/Counts FG SideBolsters  D  F 06.24.2019.xlsx', 'rb'))
# imp = pd.read_excel(open('meta/DAILY COVERAGE 6.21.19.xlsx', 'rb'))
# imp = pd.read_excel(open('meta/Foam Aunde count sheet.xlsx', 'rb'))
# imp = pd.read_excel(open('meta/Low and Out Count Sheet.xlsx', 'rb'))
# imp = pd.read_excel(open('meta/New Magna Count Sheet.XLSX', 'rb'))
# imp = pd.read_excel(open('meta/Racks Count.xlsx', 'rb'))
# imp = pd.read_excel(open('meta/Rudolph Cut Foam Sheet.xlsx', 'rb'))
# ['MaterialNumber']

def import_meta(imp):
    match_cmat=['Customer \nMaterial Number','Customer Material Number']
    match_mat=['Material Number','MaterialNumber','Part Number','Material','PO']
    match_desc=['Description','material description']

    if not 'cmat' in meta:
        meta['cmat']={}
    if not 'mat' in meta:
        meta['mat']={}
    if not 'desc' in meta:
        meta['desc']=[]
    if not 'xref' in meta:
        meta['xref']={}

    idx_cmat=None
    idx_mat=None
    idx_desc=None
    for i,v in enumerate(list(imp.columns.values)):
        if v in match_cmat:
            idx_cmat=i
        if v in match_mat:
            idx_mat=i
        if v in match_desc:
            idx_desc=i
    if (idx_cmat is None) or (idx_mat is None) or (idx_desc is None):
        for i,v in enumerate(list(imp.iloc[0])):
            if v in match_cmat and (idx_cmat is None):
                idx_cmat=i
            if v in match_mat and (idx_mat is None):
                idx_mat=i
            if v in match_desc and (idx_desc is None):
                idx_desc=i
    print('CMatCol:'+str(idx_cmat))
    print('MatCol:'+str(idx_mat))
    print('DescCol:'+str(idx_desc))

    # idx_cmat=None
    idx_mat=0
    idx_desc=1

    def prod_getcomp(p):
        comp=[]
        # print(p)
        if len(p)==15:
            if p[0].lower()=='l':
                return None
            else:
                # 550225116402478
                comp.append(p[0:2])
                comp.append(p[2:4])
                comp.append(p[4:6])
                comp.append(p[6:10])
                comp.append(p[10:12])
                comp.append(p[12:15])
        elif len(p)==12:
            if p[0].lower()=='l':
                return None
            else:
                # 110024371705
                comp.append(p[0:4])
                comp.append(p[4:8])
                comp.append(p[8:12])
        elif '-' in p:
            if len(p)==11:
                # 0200670-000
                comp.append(p[0:3])
                comp.append(p[3:7])
                comp.append(p[8:11])
            elif len(p)==6:
                # 0200670-000
                comp.append(p[0:3])
                comp.append(p[3:7])
                comp.append(p[8:11])
            else:
                return None
        else:
            return None
        return comp

    def meta_add(c,comp,p):
        if not comp[0] in meta[c]:
            meta[c][comp[0]]={}
        if not comp[1] in meta[c][comp[0]]:
            meta[c][comp[0]][comp[1]]={}
        if len(p)==15:
            if not comp[2] in meta[c][comp[0]][comp[1]]:
                meta[c][comp[0]][comp[1]][comp[2]]={}
            if not comp[3] in meta[c][comp[0]][comp[1]][comp[2]]:
                meta[c][comp[0]][comp[1]][comp[2]][comp[3]]={}
            if not comp[4] in meta[c][comp[0]][comp[1]][comp[2]][comp[3]]:
                meta[c][comp[0]][comp[1]][comp[2]][comp[3]][comp[4]]={}
            if not comp[5] in meta[c][comp[0]][comp[1]][comp[2]][comp[3]][comp[4]]:
                meta[c][comp[0]][comp[1]][comp[2]][comp[3]][comp[4]][comp[5]]={}
        elif len(p)==12:
            if p[0].lower()=='l':
                return None
            else:
                # 110024371705
                if not comp[2] in meta[c][comp[0]][comp[1]]:
                    meta[c][comp[0]][comp[1]][comp[2]]={}
                comp.append(p[8:12])
        elif '-' in p:
            if not 'rev' in meta[c][comp[0]][comp[1]]:
                meta[c][comp[0]][comp[1]]['rev']=[]
            if not comp[2] in meta[c][comp[0]][comp[1]]['rev']:
                meta[c][comp[0]][comp[1]]['rev'].append(comp[2])

    for index, r in imp.iterrows():
        ref_cmat=None
        ref_mat=None
        ref_desc=None
        if (idx_mat is not None) and (str(r[idx_mat])!='nan'):
            r[idx_mat]=str(r[idx_mat])
            comp=prod_getcomp(r[idx_mat])
            if comp is not None:
                # print(r)
                # print(r[idx_mat])
                meta_add('mat',comp,r[idx_mat])
                ref_mat=','.join(map(str,comp))
                if not ref_mat in meta['xref']:
                    meta['xref'][ref_mat]={}
        if (idx_cmat is not None) and (str(r[idx_cmat])!='nan'):
            comp=prod_getcomp(r[idx_cmat])
            if comp is not None:
                # print(comp)
                meta_add('cmat',comp,r[idx_cmat])
                ref_cmat=','.join(map(str,comp))
                if not ref_cmat in meta['xref']:
                    meta['xref'][ref_cmat]={}
            else:
                ref_cmat=r[idx_cmat]
                if not ref_cmat in meta['xref']:
                    meta['xref'][ref_cmat]={}

        if (idx_desc is not None) and (str(r[idx_desc])!='nan'):
            if not r[idx_desc] in meta['desc']:
                meta['desc'].append(r[idx_desc])
                ref_desc=len(meta['desc'])-1
            else:
                for j,w in enumerate(meta['desc']):
                     if w==r[idx_desc]:
                         ref_desc=j
                         break
        if ref_mat is not None and ref_cmat is not None and ref_mat!=ref_cmat:
            if not 'mat' in meta['xref'][ref_cmat]:
                meta['xref'][ref_cmat]['mat']=[]
            if not 'cmat' in meta['xref'][ref_mat]:
                meta['xref'][ref_mat]['cmat']=[]
            if not ref_mat in meta['xref'][ref_cmat]['mat']:
                meta['xref'][ref_cmat]['mat'].append(ref_mat)
            if not ref_cmat in meta['xref'][ref_mat]['cmat']:
                meta['xref'][ref_mat]['cmat'].append(ref_cmat)
            if ref_desc is not None:
                if not 'desc' in meta['xref'][ref_mat]:
                    meta['xref'][ref_mat]['desc']=[]
                if not 'desc' in meta['xref'][ref_cmat]:
                    meta['xref'][ref_cmat]['desc']=[]
                if not ref_desc in meta['xref'][ref_mat]['desc']:
                    meta['xref'][ref_mat]['desc'].append(ref_desc)
                if not ref_desc in meta['xref'][ref_cmat]['desc']:
                    meta['xref'][ref_cmat]['desc'].append(ref_desc)
        if ref_desc is not None:
            if ref_mat is not None:
                if not 'desc' in meta['xref'][ref_mat]:
                    meta['xref'][ref_mat]['desc']=[]
                if not ref_desc in meta['xref'][ref_mat]['desc']:
                    meta['xref'][ref_mat]['desc'].append(ref_desc)
            if ref_cmat is not None:
                if not 'desc' in meta['xref'][ref_cmat]:
                    meta['xref'][ref_cmat]['desc']=[]
                if not ref_desc in meta['xref'][ref_cmat]['desc']:
                    meta['xref'][ref_cmat]['desc'].append(ref_desc)
        # print(prod)
        # 15


# srcs=['Bader count sheet.xlsx','Counts FG SideBolsters  D  F 06.24.2019.xlsx','DAILY COVERAGE 6.21.19.xlsx','Foam Aunde count sheet.xlsx','Low and Out Count Sheet.xlsx','New Magna Count Sheet.XLSX','Racks Count.xlsx','Rudolph Cut Foam Sheet.xlsx']
# srcs=['import.xlsx']
for r, d, f in os.walk('./meta'):
    for file in f:
        if file.endswith(".xlsx"):
            print(file)
            f=open('meta/'+file,'rb')
            xls=pd.ExcelFile(f)
            sheets=xls.sheet_names
            for s in sheets:
                imp=pd.read_excel(f,sheet_name=s)
                if imp.empty:
                    continue
                # print(imp)
                import_meta(imp)
    break

# for file in srcs:
    # f=open('meta/'+file,'rb')
    # xls=pd.ExcelFile(f)
    # sheets=xls.sheet_names
    # for s in sheets:
    #     imp=pd.read_excel(f,sheet_name=s)
    #     if imp.empty:
    #         continue
    #     # print(imp)
    #     import_meta(imp)

print(json.dumps(meta,indent=2))
# exit()
meta=DictSubSortNat(**meta)
with open('meta.json','w+') as g:
    g.write(json.dumps(meta,indent=2))
exit()
# Perform Import
igntbl=[]
# ignprod=[]
# for index, row in coverage.iterrows():
#     prod=row['Component']
#     desc=row['Object description']
#     if len(prod)!=11:
#         continue
#     a=prod[0:3]
#     b=prod[3:7]
#     c=prod[8:11]
#     if a in igntbl:
#         continue
#     if not a in tables:
#         print('"'+a+'" Not in Tables')
#         igntbl.append(a)
#         continue
#     if not 'polist' in tables[a]:
#         continue
#     if not b in tables[a]['polist']:
#         print('"'+b+'" Not in "'+a+'"')
#         # ignprod.append(a)
#         continue
#     for p in tables[a]['polist']:
#         if p!=b:
#             continue
#         if not 'desc' in tables[a]['polist'][p]:
#             tables[a]['polist'][p]['desc']=''
#         if 'rev' in tables[a]['polist'][p]:
#             if not c in tables[a]['polist'][p]['rev']:
#                 tables[a]['polist'][p]['rev'].append(c)
#                 print(prod+', "'+c+'" != "'+str(tables[a]['polist'][p]['rev'])+'"')
#         if desc is not None and desc is not '':
#             if tables[a]['polist'][p]['desc']!=desc:
#                 print(prod+', "'+desc+'" != "'+tables[a]['polist'][p]['desc']+'"')
#             tables[a]['polist'][p]['desc']=desc
# with open('tables.json','w+') as g:
#     g.write(json.dumps(tables,indent=2))
# exit()
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

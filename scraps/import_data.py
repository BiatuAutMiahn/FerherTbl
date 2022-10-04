#!/usr/bin/python3
import csv
import json
import os
import time
import natsort
import csv
import random
import time
import getpass
import stdiomask
import hashlib
import os
import sys
import binascii
import base64
import json
import subprocess
import platform
import colorama
import shutil
import re
import os.path
import pdfkit
import signal
import pandas as pd
import logging
import traceback
from datetime import datetime
from time import mktime
from collections import OrderedDict
from bs4 import BeautifulSoup as bs

date="20190614"
ensure_dir("export/InactiveProdCounts")
def format_bin(string):
    if re.match("[d]\d{3}[o]",string) is not None:
        return "D{0:d}-{1:02d}-{2:d}-OF".format(int(string[1:2]),int(string[2:3]),int(string[3:4]))
    elif re.match("[d]\d{4}",string) is not None:
        return "D{0:d}-{1:02d}-{2:d}-{3:d}".format(int(string[1:2]),int(string[2:3]),int(string[3:4]),int(string[4:5]))
    elif re.match("[a-z]\d{2}",string) is not None:
        return "{0}-{1:02d}-{2:02d}".format(string[0].upper(),int(string[1]),int(string[2]))
    elif re.match("[a-z]\d[o]",string) is not None:
        return "{0}-{1:02d}-OVF".format(string[0].upper(),int(string[1]))
    elif re.match("[a-z]{2}\d[o]",string) is not None:
        return "{0}-{1:02d}-OVF".format(string[0:2].upper(),int(string[2]))
    elif string=="cfm":
        return "CUTFOAM"
    else:
        return string

def ensure_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

now=time.strftime('%Y%m%d%H%M%S',time.localtime())
tbj=open('tables.json','r')
tables=json.loads(tbj.read())
ensure_dir("data/backup/tables")
with open("data/backup/tables/"+now+".json","w+") as g:
    g.write(json.dumps(tables,indent=2))

with open('import.csv','r') as f:
    data=csv.reader(f)
    prods=[]
    for row in data:
        if len(row[0])!=11:
            continue
        if not row[0] in prods:
            prods.append(row[0])
        # print(row)
        po=row[0]
        desc=row[1]
        t=po[0:3]
        p=po[3:7]
        r=po[8:11]
        if t in tables:
            if 'polist' in tables[t]:
                if p in tables[t]['polist']:
                    if not 'rev' in tables[t]['polist'][p]:
                        tables[t]['polist'][p]['rev']=[]
                    if not r in tables[t]['polist'][p]['rev']:
                        tables[t]['polist'][p]['rev'].append(r)
                    if not 'desc' in tables[t]['polist'][p]:
                        tables[t]['polist'][p]['desc']=''
                    tables[t]['polist'][p]['desc']=desc
                    if not 'bin' in tables[t]['polist'][p]:
                        tables[t]['polist'][p]['bin']=''
                    # print('["'+t+'","'+p+'","'+r+'","'+desc+'"]')
                else:
                    print(row)
    print("---")
    # exit()
    inact={}
    for t in tables:
        if not 'polist' in tables[t]:
            continue
        for p in tables[t]['polist']:
            if not 'rev' in tables[t]['polist'][p]:
                continue
            for r in tables[t]['polist'][p]['rev']:
                if len(t+p+'-'+r)!=11:
                    continue
                if r=="???" and len(tables[t]['polist'][p]['rev'])>1:
                    continue
                if not t+p+'-'+r in prods:
                    if not t+p+'-'+r in inact:
                        inact[t+p+'-'+r]={'desc':'','counts':''}
                    if 'desc' in tables[t]['polist'][p]:
                        inact[t+p+'-'+r]['desc']=tables[t]['polist'][p]['desc']
                    # inact.append(t+p+'-'+r)
    # print(json.dumps(tables,indent=2))
    # with open('tables.json','w+') as g:
    #     g.write(json.dumps(tables,indent=2))
tbj=open('data/counts/totals_2.json','r')
tots=json.loads(tbj.read())[date]
for ia in inact:
    if ia in tots:
        # print(tots[ia])
        inact[ia]['counts']=tots[ia]

tblz=OrderedDict(natsort.natsorted(inact.items()))
new_tots={'PO':[],'Description':[],'Bin':[],'Quantity':[],'Boxes':[],'Partials':[],'Totals':[]}
for p in tblz:
    quant=None
    desc=None
    tbin=None
    if len(p)==7 or len(p)==6 or len(p)==5:
        if p[0:3] in tables:
            if p[3:] in tables[p[0:3]]['polist']:
                if 'desc' in tables[p[0:3]]['polist'][p[3:]]:
                    desc=tables[p[0:3]]['polist'][p[3:]]['desc']
                if 'bin' in tables[p[0:3]]['polist'][p[3:]]:
                    tbin=tables[p[0:3]]['polist'][p[3:]]['bin']
                quant=tables[p[0:3]]['polist'][p[3:]]['counts']
    elif len(p)==11:
        if p[0:3] in tables:
            if p[3:7] in tables[p[0:3]]['polist']:
                if 'desc' in tables[p[0:3]]['polist'][p[3:7]]:
                    desc=tables[p[0:3]]['polist'][p[3:7]]['desc']
                if 'bin' in tables[p[0:3]]['polist'][p[3:7]]:
                    tbin=tables[p[0:3]]['polist'][p[3:7]]['bin']
                quant=tables[p[0:3]]['polist'][p[3:7]]['counts']
    elif len(p)==10:
        if p[0:3] in tables:
            if p[3:6] in tables[p[0:3]]['polist']:
                if 'desc' in tables[p[0:3]]['polist'][p[3:6]]:
                    desc=tables[p[0:3]]['polist'][p[3:6]]['desc']
                if 'bin' in tables[p[0:3]]['polist'][p[3:6]]:
                    tbin=tables[p[0:3]]['polist'][p[3:6]]['bin']
                quant=tables[p[0:3]]['polist'][p[3:6]]['counts']
    elif len(p)==9:
        if p[0:3] in tables:
            if p[3:5] in tables[p[0:3]]['polist']:
                if 'desc' in tables[p[0:3]]['polist'][p[3:5]]:
                    desc=tables[p[0:3]]['polist'][p[3:5]]['desc']
                if 'bin' in tables[p[0:3]]['polist'][p[3:5]]:
                    tbin=tables[p[0:3]]['polist'][p[3:5]]['bin']
                quant=tables[p[0:3]]['polist'][p[3:5]]['counts']
    elif len(p)==12:
        if p[0:4] in tables:
            if p[8:] in tables[p[0:4]]:
                if p[4:8] in tables[p[0:4]][p[8:]]['polist']:
                    quant=tables[p[0:4]][p[8:]]['polist'][p[4:8]]['counts']
                    if 'desc' in tables[p[0:4]][p[8:]]['polist'][p[4:8]]:
                        desc=tables[p[0:4]][p[8:]]['polist'][p[4:8]]['desc']
    newt=0
    if tbin is None:
        tbin=""
    if isinstance(tblz[p],dict):# New Format with bins
        samepo=True
        print('')
        for lpo in reversed(new_tots['PO']):
            if lpo=='':
                continue
            else:
                if lpo!=p:
                    samepo=False
                else:
                    samepo=True
                break
        if len(new_tots['PO'])<1:
            samepo=False
        samepo=False
        # print(new_tots['PO'])
        # print(p+','+str(samepo))
        if 'counts' in tblz[p]['counts']:
            for c in tblz[p]['counts']['counts']:
                if '*' in c:
                    splt=c.split('*')
                    newt+=int(splt[0])*int(splt[1])
                else:
                    newt+=int(c)
        if newt>0:
            if not samepo:
                new_tots['PO'].append(p)
            else:
                new_tots['PO'].append('')
            if tbin is not None and tbin!='':
                new_tots['Bin'].append(format_bin(tbin))
            else:
                new_tots['Bin'].append("")
            if quant is not None and quant>0:
                new_tots['Quantity'].append(quant)
                new_tots['Boxes'].append(newt//quant)
                new_tots['Partials'].append(newt%quant)
            else:
                new_tots['Quantity'].append("")
                new_tots['Boxes'].append("")
                new_tots['Partials'].append("")
            if desc is not None and not samepo:
                new_tots['Description'].append(desc)
            else:
                new_tots['Description'].append("")
            new_tots['Totals'].append(newt)
        if 'ovf' in tblz[p]['counts']:
            for b in tblz[p]['counts']['ovf']:
                if len(tblz[p]['counts']['ovf'][b])>0:
                    for lpo in reversed(new_tots['PO']):
                        if lpo=='':
                            continue
                        else:
                            if lpo!=p:
                                samepo=False
                            else:
                                samepo=True
                            break
                    samepo=False
                    if not samepo:
                        new_tots['PO'].append(p)
                    else:
                        new_tots['PO'].append('')
                    newt=0
                    for c in tblz[p]['counts']['ovf'][b]:
                        if '*' in c:
                            splt=c.split('*')
                            newt+=int(splt[0])*int(splt[1])
                        else:
                            newt+=int(c)
                if newt>0:
                    new_tots['Bin'].append(format_bin(b))
                    if quant is not None and quant>0:
                        new_tots['Quantity'].append(quant)
                        new_tots['Boxes'].append(newt//quant)
                        new_tots['Partials'].append(newt%quant)
                    else:
                        # new_tots['Bin'].append("")
                        new_tots['Quantity'].append("")
                        new_tots['Boxes'].append("")
                        new_tots['Partials'].append("")
                    new_tots['Totals'].append(newt)
                    if desc is not None and not samepo:
                        new_tots['Description'].append(desc)
                    else:
                        new_tots['Description'].append('')
    else: # Legacy Fallback
        new_tots['PO'].append(p)
        newt=tblz[p]
        if quant is not None and quant is not 0:
            new_tots['Quantity'].append(quant)
            new_tots['Boxes'].append(newt//quant)
            new_tots['Partials'].append(newt%quant)
        else:
            new_tots['Quantity'].append("")
            new_tots['Boxes'].append("")
            new_tots['Partials'].append("")
        if desc is not None:
            new_tots['Description'].append(desc)
        else:
            new_tots['Description'].append("")
        new_tots['Totals'].append(newt)
# print(new_tots)
print("\rFormatting Totals...done     ")
sys.stdout.flush()
# for tt in new_tots:
#     print(tt+": "+str(len(new_tots[tt])))
print("\rGenerating Spreadsheet...",end="")
sys.stdout.flush()
stamp=time.strftime('%Y.%m.%d',time.strptime(date, '%Y%m%d'))
expf=''
expf+='_'+stamp
df = pd.DataFrame.from_dict(new_tots)

writer = pd.ExcelWriter('export/InactiveProdCounts/'+date+'.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='Inactive Counts',index=False)  # send df to writer
workbook = writer.book
#worksheet = workbook.add_worksheet('Cycle Counts')
worksheet = writer.sheets['Inactive Counts']
#worksheet.add_table('A1:'+chr(ord('A')+len(new_tots))+str(len(new_tots['PO'])))
for idx, col in enumerate(df):  # loop through all columns
    series = df[col]
    max_len = max((
        series.astype(str).map(len).max(),  # len of largest item
        len(str(series.name))  # len of column name/header
        )) + 1  # adding a little extra space
    worksheet.set_column(idx, idx, max_len)  # set column width
formatShadeRows = workbook.add_format({'border':1,
                                       'bg_color': '#E3E3E3',
                                       'font_color': 'black',
                                       'border_color': 'black'})
formatBorders = workbook.add_format({'border': 1,
                                     'border_color': 'black'})
worksheet.conditional_format('A1:'+chr(ord('A')+len(new_tots)-1)+str(len(new_tots['PO'])+1),{'type': 'formula',
                                                                          'criteria': '=MOD(ROW(),2) = 0',
                                                                          'format': formatShadeRows})
shift="2nd"
worksheet.conditional_format('A1:'+chr(ord('A')+len(new_tots)-1)+str(len(new_tots['PO'])+1),{'type': 'no_errors','format': formatBorders})
worksheet.freeze_panes(1,0)
worksheet.set_header("&L"+shift+" Shift Inactive Product Counts "+stamp+"&RPage:&P/&N",{'margin':0.3})
worksheet.fit_to_pages(1,0)
worksheet.set_margins(left=0.25,right=0.25,top=0.75,bottom=0.75)
writer.save()
print("\rGenerating Spreadsheet...done     ")
sys.stdout.flush()
# df.to_excel('csv/_'+expf+'.xlsx',date)

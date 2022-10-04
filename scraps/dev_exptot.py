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
import string
from datetime import datetime
from time import mktime
from collections import OrderedDict
from bs4 import BeautifulSoup as bs


class DictSubSortNat(OrderedDict):
    def __init__(self, **kwargs):
        super(DictSubSortNat, self).__init__()
        for key, value in natsort.natsorted(kwargs.items()):
            if isinstance(value, dict):
                self[key] = DictSubSortNat(**value)
            else:
                self[key] = value


def sort_dict(dict):
    return DictSubSortNat(**dict)

date="20190730"
dtdate=datetime.fromtimestamp(mktime(time.strptime(date,'%Y%m%d')))

totals=None
with open('data/counts/totals_2.json','r') as f:
    totals=json.loads(f.read())
totals=sort_dict(totals)
# for d in totals:
#     totals[d]=sort_dict(totals[d])

tables=None
with open('tables.json','r') as f:
    tables=json.loads(f.read())

users=None
with open('data/users.json','r') as f:
    users=json.loads(f.read())

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

def getMeta(p):
    desc=None
    quant=None
    bin=None
    if p[0:3] in tables:
        if not 'polist' in tables[p[0:3]]:
            return None
        if p[3:7] in tables[p[0:3]]['polist']:
            if 'desc' in tables[p[0:3]]['polist'][p[3:7]]:
                if tables[p[0:3]]['polist'][p[3:7]]['desc']!='':
                    desc=tables[p[0:3]]['polist'][p[3:7]]['desc']
            if 'counts' in tables[p[0:3]]['polist'][p[3:7]]:
                if tables[p[0:3]]['polist'][p[3:7]]['counts']>0:
                    quant=tables[p[0:3]]['polist'][p[3:7]]['counts']
            if 'bin' in tables[p[0:3]]['polist'][p[3:7]]:
                if tables[p[0:3]]['polist'][p[3:7]]['bin']!='':
                    bin=tables[p[0:3]]['polist'][p[3:7]]['bin']
    return desc,quant,bin

def getProdDict():
    plist={}
    for t in tables:
        if not 'polist' in tables[t]:
            continue
        for p in tables[t]['polist']:
            if 'rev' in tables[t]['polist'][p]:
                for r in tables[t]['polist'][p]['rev']:
                    plist[t+p+'-'+r]={}
            else:
                plist[t+p]={}
    return sort_dict(plist)

def getTotalsFull():
    polist=getProdDict()
    for p in polist:
        desc,quant,sbin=getMeta(p)
        if sbin==None:
            sbin="NoBin"
        if not 'desc' in polist[p]:
            polist[p]['desc']=desc
        if not 'bin' in polist[p]:
            polist[p]['bin']=sbin
        if not 'quant' in polist[p]:
            polist[p]['quant']=quant
        if not 'LastSeen' in polist[p]:
            polist[p]['LastSeen']=None
        for d in totals:
            if not d in polist[p]:
                polist[p][d]={}
            if not 'total' in polist[p][d]:
                polist[p][d]['total']=0
            if not p in totals[d]:
                continue
            if 'counts' in totals[d][p]:
                for c in totals[d][p]['counts']:
                    if not sbin in polist[p][d]:
                        polist[p][d][sbin]={}
                    if not 'total' in polist[p][d][sbin]:
                        polist[p][d][sbin]['total']=0
                    if '*' in c:
                        spl=c.split('*')
                        if not spl[0] in polist[p][d][sbin]:
                            polist[p][d][sbin][spl[0]]=0
                        polist[p][d][sbin][spl[0]]+=int(spl[1])
                        polist[p][d][sbin]['total']+=int(spl[0])*int(spl[1])
                        polist[p][d]['total']+=int(spl[0])*int(spl[1])
                    else:
                        if not c in polist[p][d][sbin]:
                            polist[p][d][sbin][c]=0
                        polist[p][d][sbin][c]+=1
                        polist[p][d]['total']+=int(c)
                        polist[p][d][sbin]['total']+=int(c)
            if 'ovf' in totals[d][p]:
                for b in totals[d][p]['ovf']:
                    for c in totals[d][p]['ovf'][b]:
                        if not b in polist[p][d]:
                            polist[p][d][b]={}
                        if not 'total' in polist[p][d][b]:
                            polist[p][d][b]['total']=0
                        if '*' in c:
                            spl=c.split('*')
                            if not spl[0] in polist[p][d][b]:
                                polist[p][d][b][spl[0]]=0
                            polist[p][d][b][spl[0]]+=int(spl[1])
                            polist[p][d]['total']+=int(spl[0])*int(spl[1])
                            polist[p][d][b]['total']+=int(spl[0])*int(spl[1])
                        else:
                            if not c in polist[p][d][b]:
                                polist[p][d][b][c]=0
                            polist[p][d][b][c]+=1
                            polist[p][d][b]['total']+=int(c)
                            polist[p][d]['total']+=int(c)
            if polist[p][d]['total']>0:
                polist[p]['LastSeen']=d
    # with open('test.json','w+') as z:
    #     z.write(json.dumps(sort_dict(polist),indent=2))
    return sort_dict(polist)

def getCoverage(fullTotals,d):
    cvg=[]
    cvglast=None
    for p in fullTotals:
        if not d in fullTotals[p]:
            continue
        if p[0:3]==cvglast:
            continue
        if p[0:3] not in cvg and fullTotals[p][d]['total']>0:
            cvg.append(p[0:3])
    return sorted(cvg)
# print(json.dumps(getTotalsFull(),indent=2))

def expTotals(shift):
    blanksame=False
    expf="Cycles_"+shift
    print("Processing Totals...",end="")
    sys.stdout.flush()
    fullTotals=getTotalsFull()
    print("\rProcessing Totals...done")
    print("Formatting Totals...",end="")
    sys.stdout.flush()
    export={
        'Cycle Counts' : {'PO':[],'Description':[],'Bin':[],'StdPack':[],'Boxes':[],'PartialQty':[],'Total':[]},
        'Cycle Counts (No Bin)' : {'PO':[],'Description':[],'StdPack':[],'Boxes':[],'PartialQty':[],'Total':[]},
        '5 Day Coverage': {'PO':[],'Description':[],'Last Seen':[]},
        "Low Counts": {'PO':[],'Description':[],'Bin':[],'StdPack':[],'Boxes':[],'PartialQty':[],'Total':[]} # ,'Last Coverage Date':[]
    }
        # "Dormancy": {'PO':[],'Description':[],'Last Covered':[],'First Seen':[],'Duration':[],'Bin':[],'StdPack':[],'Boxes':[],'PartialQty':[],'Total':[]}
    samepo=False
    dates=list(totals.keys())
    dates=dates[dates.index(date)-4:dates.index(date)+1][::-1]
    lastSeen=date
    for d in dates:
        tdate=time.strftime('%Y.%m.%d',time.strptime(d,'%Y%m%d'))
        if not tdate in list(export['5 Day Coverage'].keys()):
            export['5 Day Coverage'][tdate]=[]

    # print(json.dumps(lastCvg,indent=2))
    for p in fullTotals:
        # print("")
        if p!=samepo:
            samepo=False
        desc=fullTotals[p]['desc']
        if desc==None:
            desc=""
        sbin=fullTotals[p]['bin']
        if sbin==None:
            sbin="NoBin"
        quant=fullTotals[p]['quant']
        if quant==None:
            quant=""
        # 5 Day Coverage
        if fullTotals[p]['LastSeen']!=None:
            export['5 Day Coverage']['PO'].append(p)
            export['5 Day Coverage']['Description'].append(desc)
            export['5 Day Coverage']['Last Seen'].append(time.strftime('%Y.%m.%d',time.strptime(fullTotals[p]['LastSeen'],'%Y%m%d')))
            for d in dates:
                tdate=time.strftime('%Y.%m.%d',time.strptime(d,'%Y%m%d'))
                export['5 Day Coverage'][tdate].append(fullTotals[p][d]['total'])

            # if firstSeen!=None:
            #     firstdt=datetime.fromtimestamp(mktime(time.strptime(firstSeen,'%Y%m%d')))
            #     lastdt=datetime.fromtimestamp(mktime(time.strptime(lastSeen,'%Y%m%d')))
            #     tdelta=lastdt-firstdt
            #     if tdelta.days>=5:
            #         # print(p+','+b)
            #         # print("    "+str(tdelta.days))
            #         export["Dormancy"]['PO'].append(p)
            #         export["Dormancy"]['Description'].append(desc)
            #         export["Dormancy"]['First Seen'].append(time.strftime('%Y.%m.%d',time.strptime(firstSeen,'%Y%m%d')))
            #         export["Dormancy"]['Bin'].append(format_bin(b))
            #         export["Dormancy"]['Duration'].append(str(tdelta.days)+' Days')
            #         export["Dormancy"]['StdPack'].append(str(quant))
            #         export["Dormancy"]['Total'].append(fullTotals[p][d][b]['total'])
            #         if quant!="":
            #             export["Dormancy"]['Boxes'].append(fullTotals[p][d][b]['total']//quant)
            #             export["Dormancy"]['PartialQty'].append(fullTotals[p][d][b]['total']%quant)
            #         else:
            #             export["Dormancy"]['Boxes'].append("")
            #             export["Dormancy"]['PartialQty'].append("")


        # Cycle Counts, Cycle Counts (No Bin)
        if not date in fullTotals[p]:
            continue
        # Low 'n Out
        # !! Will return everything that was not counted !!
        if sbin!='NoBin':
            bquant=quant
            if quant=="":
                bquant=0
            if fullTotals[p][date]['total']>0 and fullTotals[p][date]['total']<=int(bquant)*3:
                export["Low Counts"]['PO'].append(p)
                export["Low Counts"]['Bin'].append(format_bin(sbin))
                export["Low Counts"]['Description'].append(desc)
                export["Low Counts"]['Total'].append(fullTotals[p][date]['total'])
                export["Low Counts"]['StdPack'].append(quant)
                if quant!="":
                    export["Low Counts"]['Boxes'].append(fullTotals[p][date]['total']//quant)
                    export["Low Counts"]['PartialQty'].append(fullTotals[p][date]['total']%quant)
                else:
                    export["Low Counts"]['Boxes'].append("")
                    export["Low Counts"]['PartialQty'].append("")

        # "Dormancy": {'PO':[],'Description':[],'First Seen':[],'Duration':[],'Bin':[],'StdPack':[],'Boxes':[],'PartialQty':[],'Total':[]}
        # for d in fullTotals[p]:
        #     if d in ['desc','bin','quant','LastSeen']:
        #         continue

        if fullTotals[p][date]['total']>0:
            export['Cycle Counts (No Bin)']['PO'].append(p)
            export['Cycle Counts (No Bin)']['Description'].append(desc)
            export['Cycle Counts (No Bin)']['Total'].append(fullTotals[p][date]['total'])
            export['Cycle Counts (No Bin)']['StdPack'].append(quant)
            if quant!="":
                export['Cycle Counts (No Bin)']['Boxes'].append(fullTotals[p][date]['total']//quant)
                export['Cycle Counts (No Bin)']['PartialQty'].append(fullTotals[p][date]['total']%quant)
            else:
                export['Cycle Counts (No Bin)']['Boxes'].append("")
                export['Cycle Counts (No Bin)']['PartialQty'].append("")
            for b in fullTotals[p][date]:
                if b=="total":
                    continue
                export['Cycle Counts']['Bin'].append(format_bin(b))
                if not samepo:
                    export['Cycle Counts']['PO'].append(p)
                    export['Cycle Counts']['Description'].append(desc)
                    if blanksame:
                        export['Cycle Counts']['Total'].append(fullTotals[p][date]['total'])
                    else:
                        export['Cycle Counts']['Total'].append(fullTotals[p][date][b]['total'])
                    export['Cycle Counts']['StdPack'].append(quant)
                    if quant!="":
                        export['Cycle Counts']['Boxes'].append(fullTotals[p][date][b]['total']//quant)
                        export['Cycle Counts']['PartialQty'].append(fullTotals[p][date][b]['total']%quant)
                    else:
                        export['Cycle Counts']['Boxes'].append("")
                        export['Cycle Counts']['PartialQty'].append("")
                    if blanksame:
                        samepo=p
                else:
                    export['Cycle Counts']['PO'].append("")
                    export['Cycle Counts']['Description'].append("")
                    export['Cycle Counts']['Total'].append("")
                    export['Cycle Counts']['StdPack'].append(quant)
                    if quant!="":
                        export['Cycle Counts']['Boxes'].append(fullTotals[p][date][b]['total']//quant)
                        export['Cycle Counts']['PartialQty'].append(fullTotals[p][date][b]['total']%quant)
                    else:
                        export['Cycle Counts']['Boxes'].append("")
                        export['Cycle Counts']['PartialQty'].append("")
    print("\rFormatting Totals...done")
    print("Generating Spreadsheet...",end="")
    sys.stdout.flush()
    for tt in export['Cycle Counts']:
        print(tt+": "+str(len(export['Cycle Counts'][tt])))
    sys.stdout.flush()
    stamp=time.strftime('%Y.%m.%d',time.strptime(date, '%Y%m%d'))
    expf+='_'+stamp
    writer = pd.ExcelWriter('export/'+expf+'.xlsx', engine='xlsxwriter')
    wkbk = writer.book
    formatShadeRows = wkbk.add_format({'border':1,'bg_color': '#E3E3E3','font_color': 'black','border_color': 'black'})
    formatBorders = wkbk.add_format({'border': 1,'border_color': 'black'})
    formatGreen = wkbk.add_format({'border':1,'bg_color': '#00ff87','font_color': 'black','border_color': 'black'})
    formatYellow = wkbk.add_format({'border':1,'bg_color': '#ffff5f','font_color': 'black','border_color': 'black'})
    formatRed = wkbk.add_format({'border':1,'bg_color': '#ff5f5f','font_color': 'black','border_color': 'black'})
    for sheet in export:
        df=pd.DataFrame.from_dict(export[sheet])
        df.to_excel(writer, sheet_name=sheet,index=False)
        if sheet=='Dormancy':
            print(df)
        wksht = writer.sheets[sheet]
        if sheet=='5 Day Coverage':
            for idx,cell in enumerate(df['Last Seen']):
                lastdt=datetime.fromtimestamp(mktime(time.strptime(df['Last Seen'][idx],'%Y.%m.%d')))
                tdelta=dtdate-lastdt
                # print(str(idx)+','+df['Last Seen'][idx]+','+str(tdelta.days))
                if tdelta.days<=6:
                    wksht.conditional_format('C'+str(idx+2),{'type': 'no_errors','format': formatGreen})
                elif tdelta.days>=21:
                    wksht.conditional_format('C'+str(idx+2),{'type': 'no_errors','format': formatRed})
                elif tdelta.days>=7:
                    wksht.conditional_format('C'+str(idx+2),{'type': 'no_errors','format': formatYellow})
            # print(df.shape[0])
        for idx, col in enumerate(df):
            series = df[col]
            max_len = max((series.astype(str).map(len).max(),len(str(series.name)))) + 1
            wksht.set_column(idx, idx, max_len)
        wksht.conditional_format(0,0,df.shape[0],df.shape[1]-1,{'type': 'formula','criteria': '=MOD(ROW(),2) = 0','format': formatShadeRows})
        wksht.conditional_format(0,0,df.shape[0],df.shape[1]-1,{'type': 'no_errors','format': formatBorders})
        wksht.freeze_panes(1,0)
        wksht.fit_to_pages(1,0)
        wksht.set_header("&L"+shift+" Shift "+sheet+" "+stamp+"&RPage:&P/&N",{'margin':0.1})
        wksht.set_margins(left=0.25,right=0.25,top=0.5,bottom=0.0)
    writer.save()
    print("\rGenerating Spreadsheet...done     ")
    sys.stdout.flush()
    print("Download Here: https://fehrertbl.infinitycommunicationsgateway.net/export/"+expf+".xlsx")

expTotals('2nd')

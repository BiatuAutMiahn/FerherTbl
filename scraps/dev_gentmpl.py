#!/usr/bin/python3
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
from collections import OrderedDict
from bs4 import BeautifulSoup as bs
try:
    import readline
except ImportError:
    pass

colorama.init(autoreset=True)


def natural_key(string_):
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]

class DictSubSortNat(OrderedDict):
    def __init__(self, **kwargs):
        super(DictSubSortNat, self).__init__()
        for key, value in natsort.natsorted(kwargs.items()):
            if isinstance(value, dict):
                self[key] = DictSubSortNat(**value)
            else:
                self[key] = value

class DictSubSortNatLen(OrderedDict):
    def __init__(self, **kwargs):
        super(DictSubSortNatLen, self).__init__()
        for key, value in natsort.natsorted(kwargs.items(),key=lambda x: len(str(x[1])),reverse=True):
            if isinstance(value, dict):
                self[key] = DictSubSortNatLen(**value)
            else:
                self[key] = value

class DictSubSortNat(OrderedDict):
    def __init__(self, **kwargs):
        super(DictSubSortNat, self).__init__()
        for key, value in natsort.natsorted(kwargs.items()):
            if isinstance(value, dict):
                self[key] = DictSubSortNat(**value)
            else:
                self[key] = value

class DictSubSortNatLen2(OrderedDict):
    def __init__(self, **kwargs):
        super(DictSubSortNatLen2, self).__init__()
        for key, value in natsort.natsorted(kwargs.items(),key=lambda x: len(str(x[1])),reverse=True):
            if isinstance(value, list):
                self[key] = DictSubSortNatLen2(**value)
            else:
                self[key] = value

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

def build_templ():
    options = {
        'page-size': 'Letter',
        'margin-top': '0.2in',
        'margin-right': '0.0in',
        'margin-bottom': '0.0in',
        'margin-left': '0.2in',
        'zoom': '1.17',
        'no-outline': None,
        'quiet': ''
    }

    layout={
        "default":{
            'cols':6,
            'plines':6,
            'spaces':4,
            'norev': False,
        },
        "090":{
            'cols':4,
            'plines':6,
            'spaces':4,
            'norev': False,
        },
        "161":{
            'cols':6,
            'plines':6,
            'spaces':4,
            'norev': True,
        },
        "122":{
            'cols':6,
            'plines':6,
            'spaces':4,
            'norev': True,
        },
        "126":{
            'cols':6,
            'plines':6,
            'spaces':4,
            'norev': True,
        },
        "625":{
            'cols':6,
            'plines':6,
            'spaces':4,
            'norev': True,
        },
        "16S":{
            'cols':6,
            'plines':6,
            'spaces':4,
            'norev': True,
        },
        "383":{
            'cols':4,
            'plines':6,
            'spaces':4,
            'norev': False,
        }
    }

    cols=layout['default']['cols']
    plines=layout['default']['plines']
    spaces=layout['default']['spaces']
    tables=None
    const_cell_width=7.3983 # 1.0569/Cell

    blank_html='''
                <!DOCTYPE html>
                <html>
                    <head>
                        <link href="https://fonts.googleapis.com/css?family=Inconsolata" rel="stylesheet">
                		<style>
                			body {
                				width: 21cm;
                				background-color: white;
                				font-family: 'Inconsolata', monospace;
                				font-size: 14pt;
                				font-weight:400;
                			}

                			@media print {
                				body {
                					width: 21cm;
                					/* height: 29.7cm; */

                				}
                			}
                            @media print {
                                html, body {
                                    height: 99%;
                                }
                            }
                        </style>
                    </head>
                    <body>
                    &nbsp;
                    </body>
                </html>
    '''

    def gen_html(ccols,cspaces):
        head='''
            <!DOCTYPE html>
            <html>
                <head>
                    <link href="https://fonts.googleapis.com/css?family=Inconsolata" rel="stylesheet">
            		<style>
            			body {
            				width: 21cm;
            				background-color: white;
            				font-family: 'Inconsolata', monospace;
            				font-size: 14pt;
            				font-weight:400;
            			}

            			@media print {
            				body {
            					width: 21cm;
            					/* height: 29.7cm; */

            				}
            			}
                        @media print {
                            html, body {
                                height: 99%;
                            }
                        }
            			.uline {
            				text-decoration: underline;
            			}

            			.own-detail-wrap {
            				margin: 0 0 2.5mm 10mm;
            			}
            			.own-detail {
            				padding: 2mm;
            			}
            			table {
            				border-collapse: collapse;
            				border-spacing: 0;
            				empty-cells: show;
            			}

            			tr {
            				display: table-row;
            				vertical-align: inherit;
            				border-color: inherit;
            				line-height:2mm;
            			}
            			td, th {
            				vertical-align: top;
            				font-size: 12pt;
            			}
            			.tbl-cell-root,.tbl-cell-head,.tbl-cell,.tbl-cell-hide {
            				line-height:0mm;
            				text-align: center;
            			}
            			.tbl-cell-root,.tbl-cell-hide {
            				width: 0.6in;
            			}
            			.tbl-cell-head,.tbl-cell {
            				width:'''+str(const_cell_width/ccols)+'''in;
            			}
            			.tbl-cell-root,.tbl-cell-head,.tbl-cell {
            				border-left-width: 0.06cm;
            				border-left-style: solid;
            				border-left-color: #000000;
            				border-right-style: none;
            				border-top-width: 0.06cm;
            				border-top-style: solid;
            				border-top-color: #000000;
            				border-bottom-width: 0.06cm;
            				border-bottom-style: solid;
            				border-bottom-color: #000000;
            			}
            			.tbl-cell {
            				border-bottom-color: #c7c7c7;
            				/* line-height: 7.1mm; */
            			}
            			.tbl-cell-foot {
            				border-bottom-color: #000000;
            			}

            			.tbl-cell-fill {
            				background-color: #000000;
            				color: #ffffff;
            			}
            			.tbl-detail {
            				display: inline;
            				border-left-width: 0.06cm;
            				border-left-style: solid;
            				border-left-color: #000000;
            				border-top-width: 0.06cm;
            				border-top-style: solid;
            				border-top-color: #000000;
            				border-right-width: 0.06cm;
            				border-right-style: solid;
            				border-right-color: #000000;
            				width: 0.6in;
            				padding: 0.02in;
            			}

            			.hide{
            				display:none;
            			}
            			.tbl-cell-head {
            				/* font-size: 18pt; */
            			}
            			.tbl-row-last {
            				border-right-width: 0.06cm;
            				border-right-style: solid;
            				border-right-color: #000000;
            			}
                        .tbl-cell-head.tbl-cell-fill:not(:nth-child(2)) {
                            border-left-color: #ffffff;
                        }
            		</style>
                </head>
                <body>
                    <div class="own-detail-wrap">
                        <div class="own-date own-detail">
                            <span>Date: </span><!--
                            --><span class="uline">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><!--
                            --><span>.</span><!--
                            --><span class="uline">&nbsp;&nbsp;&nbsp;</span><!--
                            --><span>.</span><!--
                            --><span class="uline">&nbsp;&nbsp;&nbsp;</span>
                        </div>
                        <div class="own-name own-detail">
                            <span>Name: </span><!--
                            --><span class="uline">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
                        </div>
                    </div>
                    <div class="tbl-wrap">
        '''

        numfields=''
        for i in range(1,cspaces):
            numfields+='''
                       <tbody>
                          <tr>
            '''
            numfields+='''
                <td class="tbl-cell-hide">
                    <p class="tbl-cell-space">&nbsp;</p>
                </td>
            '''
            for j in range(1,ccols):
                numfields+='''
                    <td class="tbl-cell">
                        <p class="tbl-cell-space">&nbsp;</p>
                    </td>
                '''
            numfields+='''
                    <td class="tbl-cell tbl-row-last">
                        <p class="tbl-cell-space">&nbsp;</p>
                    </td>
                </tr>
            '''
            numfields+='''
               </tbody>
            '''
        numfields+='''
                   <tbody>
                      <tr>
        '''
        numfields+='''
            <td class="tbl-cell-hide">
                <p class="tbl-cell-space">&nbsp;</p>
            </td>
        '''
        for j in range(1,ccols):
            numfields+='''
                <td class="tbl-cell tbl-cell-foot">
                    <p class="tbl-cell-space">&nbsp;</p>
                </td>
            '''
        numfields+='''
                <td class="tbl-cell tbl-cell-foot tbl-row-last">
                    <p class="tbl-cell-space">&nbsp;</p>
                </td>
            </tr>
        '''
        numfields+='''
           </tbody>
        '''
        return head,numfields
    print("Reading Tables...",end="")
    sys.stdout.flush()
    if os.path.isfile('tables.json'):
        with open('tables.json') as f:
            tables=json.loads(f.read())
    print("\rReading Tables...done")
    print("Processing Tables...",end="")
    sys.stdout.flush()
    tables=DictSubSortNat(**tables)
    templ={}
    # Reformat Trim(383)
    trim={'polist':{}}
    for i in range(2,5):
        if i==2:
            for j in range(1,6):
                for k in range(1,4):
                    trim['polist'][format_bin('d'+str(i)+str(j)+str(k)+'o')]={}
        if i==3:
            for j in range(1,7):
                if j in [1,2,3,4]:
                    for k in range(1,4):
                        for l in range(1,7):
                            if (j==1 and k==3 and l>5) or (j==2 and ((k==1 and l>5) or (k==2 and l in [2,4])) or (j==3 and k==1 and l==3)):
                                continue
                            trim['polist'][format_bin('d'+str(i)+str(j)+str(k)+str(l))]={}
                    for k in [4,5]:
                        trim['polist'][format_bin('d'+str(i)+str(j)+str(k)+'o')]={}
                else:
                    for k in range(1,4):
                        trim['polist'][format_bin('d'+str(i)+str(j)+str(k)+'o')]={}
        if i==4:
            for j in range(1,6):
                for k in range(1,5):
                    trim['polist'][format_bin('d'+str(i)+str(j)+str(k)+'o')]={}
    #tables['383']=trim
    for t in tables:
        cols=layout['default']['cols']
        plines=layout['default']['plines']
        spaces=layout['default']['plines']
        norev=layout['default']['norev']
        if t in layout:
             cols=layout[t]['cols']
             plines=layout[t]['plines']
             spaces=layout[t]['plines']
             norev=layout[t]['norev']
        if 'polist' in tables[t]:
            if not t in templ:
                templ[t]={'lines':{}}
            l=0
            j=0
            for po in tables[t]['polist']:
                if 'rev' in tables[t]['polist'][po]:
                    for r in tables[t]['polist'][po]['rev']:
                        if j==cols:
                            l+=1
                            j=0
                        if not l in templ[t]['lines']:
                            templ[t]['lines'][l]=[]
                        templ[t]['lines'][l].append(po+'-'+r)
                        j+=1
                else:
                    if j==cols:
                        l+=1
                        j=0
                        # print(str(p)+','+str(l)+','+str(j))
                    if not l in templ[t]['lines']:
                        templ[t]['lines'][l]=[]
                    if t in ['383']:
                        templ[t]['lines'][l].append(po)
                    else:
                        if norev:
                            templ[t]['lines'][l].append(po)
                        else:
                            templ[t]['lines'][l].append(po+'-???')
                    j+=1
            if j<cols:
                while True:
                    if j==cols:
                        break;
                    templ[t]['lines'][l].append("")
                    j+=1
        else:
            pass
    templ=DictSubSortNatLen2(**templ)
    p=0
    i=0
    j=0
    pol=''
    pages={}
    for po in templ:
        if not 'lines' in templ[po]:
            continue
        cols=layout['default']['cols']
        plines=layout['default']['plines']
        spaces=layout['default']['plines']
        if po in layout:
             cols=layout[po]['cols']
             plines=layout[po]['plines']
             spaces=layout[po]['plines']
        if pol!=po:
            cols=layout['default']['cols']
            plines=layout['default']['plines']
            spaces=layout['default']['plines']
            if pol in layout:
                 cols=layout[pol]['cols']
                 plines=layout[pol]['plines']
                 spaces=layout[pol]['plines']
            if j>plines:
                if not p in pages:
                    pages[p]={}
                if not pol in pages[p]:
                    pages[p][pol]={'lines':{}}
                for x in range(i,plines):
                    for y in range(1,cols):
                        if len(pages[p][pol]['lines'][l])==cols:
                            l+=1
                        if not l in pages[p][pol]['lines']:
                            pages[p][pol]['lines'][l]=[]
                        pages[p][pol]['lines'][l].append("")
                    if len(pages[p][pol]['lines'][l])<cols:
                        for y in range(len(pages[p][pol]['lines'][l]),cols):
                            pages[p][pol]['lines'][l].append("")
                p+=1
                i=0
            j=0
            pol=po
        if i>=5:
            p+=1
            i=0
        for l in templ[po]['lines']:
            if i==plines:
                p+=1
                i=0
            if not p in pages:
                pages[p]={}
            if not po in pages[p]:
                pages[p][po]={'lines':{}}
            if not l in pages[p][po]['lines']:
                pages[p][po]['lines'][l]=[]
            pages[p][po]['lines'][l]=templ[po]['lines'][l]
            j+=1
            i+=1
    pagemap={}
    pg=1
    tl=''
    pgmax=1
    for p in pages:
        pgtmap=[]
        tt=''
        for t in pages[p]:
            pgtmap.append(t)
            tt=t
        if len(pgtmap)==1:
            pagemap[p]=[tt,pg,pgmax]
    tt=''
    tl=''
    if len(list(pagemap))>1:
        for i,pp in enumerate(pagemap):
            if tl!=pagemap[pp][0]:
                tt=pagemap[pp][0]
            else:
                pagemap[pp][1]+=pagemap[list(pagemap)[i-1]][1]
            for ppa in pagemap:
                if pp==ppa:
                    continue
                if tt==pagemap[ppa][0]:
                    pagemap[ppa][2]+=1
                    tl=tt

    # exit()
    misc=[]
    lastt=''
    html=''
    pg=1
    pgl=''
    # print(json.dumps(pages,indent=2))
    print("\rProcessing Tables...done")
    print("Generating Templates...",end='')
    sys.stdout.flush()
    # for type in ['static','olow','ohi']
    for p in pages:
        rootl=''
        ccols=layout['default']['cols']
        cspaces=layout['default']['spaces']
        for x in pagemap:
            if p==x:
                if pagemap[p][0] in layout:
                    ccols=layout[pagemap[p][0]]['cols']
                    cspaces=layout[pagemap[p][0]]['spaces']
                    #
                    # pagemap[p][0]+','+str(ccols)+','+str(cspaces))
                else:
                    pass
                    # print(str(p)+','+str(ccols)+','+str(cspaces))
            else:
                pass
            # print(str(p)+','+str(ccols)+','+str(cspaces))
        #         print(pagemap[p][0]+','+str(ccols)+','+str(cspaces))
        # print(str(ccols)+','+str(cspaces))

        htmlhead,numfields=gen_html(ccols,cspaces)
        html=htmlhead
        # if int(key) >= 1100 or pages>1 and False:
        #     html+='''
        #         <div class="tbl-detail-wrap">
        #     '''
        # else:
        if p in pagemap:
            html+='''
                <div class="tbl-detail-wrap">
            '''
            # if int(key) >= 1100 and False:
            #     html+='''
            #         <div class="tbl-detail eleven-ins">'''+key+'''</div>
            #     '''
            # else:
            html+='''
                <div class="tbl-detail page-ins">&nbsp;Page '''+str(pagemap[p][1])+'''/'''+str(pagemap[p][2])+'''</div>
            '''
            if type:
                if type=='static':
                    html+='''
                        <div class="tbl-detail eleven-ins">&nbsp;Static Bin&nbsp;</div>
                    '''
                if type=='olow':
                    html+='''
                        <div class="tbl-detail eleven-ins">&nbsp;Overflow High&nbsp;</div>
                    '''
                if type=='ohi':
                    html+='''
                        <div style="margin:0.1em" class="tbl-detail eleven-ins">&nbsp;Overflow Low&nbsp;</div>
                    '''
            else:
                html+='''
                    <div style="margin:0.1em" class="tbl-detail eleven-ins hide">&nbsp;</div>
                '''
            html+='''
            </div>
            '''
        else:
            html+='''
                <div class="tbl-detail-wrap hide">
            '''
            html+='''
                <div class="tbl-detail eleven-ins hide"></div>
            '''
            html+='''
                <div class="tbl-detail page-ins hide"></div>
            </div>
            '''
        # html+='''
        #     <div class="tbl-detail page-ins hide"></div>
        # </div>
        # '''
        html+='''
            <table class="tbl" border="0" cellspacing="0" cellpadding="0">
        '''
        for t in pages[p]:
            for ll in pages[p][t]['lines']:
                if t==rootl:
                    html+='''
                        <tbody>
                            <tr>
                                <td class="tbl-cell-hide">
                                    <p class="tbl-cell-space">&nbsp;</p>
                                </td>
                    '''
                else:
                    html+='''
                        <tbody>
                            <tr>
                                <td class="tbl-cell-root">
                                    <p class="tbl-cell-space">'''+t+'''</p>
                                </td>
                    '''
                    rootl=t
                for l in pages[p][t]['lines'][ll]:
                    if l==pages[p][t]['lines'][ll][-1]:
                        if l=="":
                            html+='''
                                     <td class="tbl-cell-head tbl-row-last">
                                        <p class="tbl-cell-space">&nbsp;</p>
                                     </td>
                            '''
                        else:
                            html+='''
                                 <td class="tbl-cell-head tbl-row-last tbl-cell-fill">
                                    <p class="tbl-cell-space">'''+l+'''</p>
                                 </td>
                            '''
                    else:
                        if l=="":
                            html+='''
                                     <td class="tbl-cell-head">
                                        <p class="tbl-cell-space">&nbsp;</p>
                                     </td>
                            '''
                        else:
                            html+='''
                                     <td class="tbl-cell-head tbl-cell-fill">
                                        <p class="tbl-cell-space">'''+l+'''</p>
                                     </td>
                            '''
                html+='''
                          </tr>
                       </tbody>
                '''
                html+=numfields
        html+='''
                        </table>
                    </div>
                </body>
            </html>
        '''
        fname=''
        if p in pagemap:
            fname=str(pagemap[p][0])+'.'+str(pagemap[p][1])
        else:
            fname=str(p)
            misc.append(fname)
        with open('html/'+fname+".html", 'w') as outfile:
            soup = bs(html,features="html.parser")
            html=soup.prettify(formatter="html")
            outfile.write(html)
            outfile.close()
    pdf={}
    pmap=[]
    j=0
    for i,pp in enumerate(pagemap):
        if not j in pdf:
            pdf[j]=[]
        if i>0:
            if pagemap[list(pagemap)[i-1]][0]==pagemap[pp][0]:
                pdf[j].append('html/'+pagemap[pp][0]+'.'+str(pagemap[pp][1])+'.html')
            else:
                j+=1
                if not j in pdf:
                    pdf[j]=[]
                pdf[j].append('html/'+pagemap[pp][0]+'.'+str(pagemap[pp][1])+'.html')

        else:
            pdf[j].append('html/'+pagemap[pp][0]+'.'+str(pagemap[pp][1])+'.html')
        if not pagemap[pp][0] in pmap:
            pmap.append(pagemap[pp][0])
    j+=1
    if not j in pdf:
        pdf[j]=[]
    for m in misc:
        pdf[j].append('html/'+m+'.html')

    pmap.append('misc')
    print("\rGenerating Templates...done")
    # insert pages for printouts
    for p in pdf:
        res=[]
        for i,x in enumerate(pdf[p]):
            res.append(x)
            res.append('html/blank.html')
        for i,x in enumerate(pdf[p]):
            res.append(x)
            res.append(x)
        pdf[p]=res
    # print(json.dumps(pdf,indent=4))
    with open('html/blank.html','w+') as f:
        f.write(blank_html)
    for i,p in enumerate(pdf):
        print("Generating "+pmap[i]+".pdf",end='')
        sys.stdout.flush()
        pdfkit.from_file(pdf[p],"pdf/"+pmap[i]+".pdf",options=options)
        print("\rGenerating "+pmap[i]+".pdf...done")
    print("Download Here: https://fehrertbl.infinitycommunicationsgateway.net/pdf/")


build_templ()

#!/usr/bin/python3
import sys
print("Initializing...")
sys.stdout.flush()
import natsort
import csv
import random
import time
import getpass
import stdiomask
import hashlib
import os
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
import InfCommon as Inf
from datetime import datetime
from time import mktime
from collections import OrderedDict
from bs4 import BeautifulSoup as bs
try:
    import readline
except ImportError:
    pass

build='20190620213410'
build=time.strftime('%Y.%m.%d',time.strptime(build, '%Y%m%d%H%M%S'))
LICENSE='''
Infinity.FehrerTbl is property of Christopher A Gordon, founder of
InfinityResearchAndDevlopment. By using this software you agree
to the following terms and conditions. This software is free to
use personally and commercially. Any unauthorized use of this
software beyond it's intended use is prohibited. Redistribution,
Modification, decompilation, and reverse engineering this software
is prohibited. This software is open source and is available upon
request. The information stored by this software is the
intellectual property of FS Fehrer Automotive GmbH, ResourceMFG,
Prologistix, and InfinityResearchAndDevelopment.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,')
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

Software used in Infinity.FehrerTbl:
Python     : https://docs.python.org/3/license.html
stdiomask  : https://github.com/asweigart/stdiomask/blob/master/LICENSE.txt
colorama   : https://github.com/tartley/colorama/blob/master/LICENSE.txt
ttyd       : https://github.com/tsl0922/ttyd/blob/master/LICENSE
pandas     : http://pandas.pydata.org/pandas-docs/stable/getting_started/overview.html#license
xlsxwriter : https://xlsxwriter.readthedocs.io/license.html
natsort    : https://github.com/SethMMorton/natsort/blob/master/LICENSE
pdfkit     : https://github.com/JazzCore/python-pdfkit/blob/master/LICENSE
bs4        : https://bazaar.launchpad.net/~leonardr/beautifulsoup/bs4/view/head:/LICENSE
'''

def hash_password(password):
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('utf-8')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return base64.urlsafe_b64encode((salt + pwdhash)).decode('utf-8')

def verify_password(stored_password, provided_password):
    stored_password=base64.b64decode(stored_password.encode("utf-8"))
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',provided_password.encode('utf-8'),salt,100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash.encode("utf-8") == stored_password

def loginauth(username, password):
    if username in users:
        read_userdat()
        if verify_password(userdat["key"],password):
            print("Login successful")
            return True
    return False

def login():
    global user
    while True:
        username = input("User: ")
        if len(username) > 0:
            break
    user=username
    while True:
        password = stdiomask.getpass()
        if len(password) > 0:
            break
    if loginauth(username, password):
        # user=username
        return True
    else:
        user=None
        return False

def fail_login():
    exit()

def hascounts(table,prod=None):
    if table in usertbl:
        if 'polist' in usertbl[table]:
            if prod==None:
                for prod in usertbl[table]['polist']:
                    if prod in usertbl[table]['polist']:
                        if 'ovf' in usertbl[table]['polist'][prod]:
                            for b in usertbl[table]['polist'][prod]['ovf']:
                                if len(usertbl[table]['polist'][prod]['ovf'][b])>0:
                                    return True
                        if 'counts' in usertbl[table]['polist'][prod]:
                            if len(usertbl[table]['polist'][prod]['counts'])>0:
                                return True
            else:
                if prod in usertbl[table]['polist']:
                    if 'ovf' in usertbl[table]['polist'][prod]:
                        for b in usertbl[table]['polist'][prod]['ovf']:
                            if len(usertbl[table]['polist'][prod]['ovf'][b])>0:
                                return True
                    if 'counts' in usertbl[table]['polist'][prod]:
                        if len(usertbl[table]['polist'][prod]['counts'])>0:
                            return True
    return False


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
                <div class="tbl-detail eleven-ins hide"></div>
            '''
            html+='''
                <div class="tbl-detail page-ins">Page '''+str(pagemap[p][1])+'''/'''+str(pagemap[p][2])+'''</div>
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

def sync_tables(pull=False,push=False):
    print("\rSyncing Tables...",end="")
    sys.stdout.flush()
    global tables
    if os.path.isfile("tables.lock"):
        print("\rSyncing Tables, Waiting...",end="")
        sys.stdout.flush()
        while True:
            if not os.path.isfile("tables.lock"):
                break
            time.sleep(0.1)
    open("tables.lock",'a').close()
    if os.path.isfile("tables.json"):
        if not push:
            with open("tables.json") as f:
                new_tables=json.loads(f.read())
                new_tables.update(tables)
                tables=new_tables
        sort_tables()
        if not pull:
            with open("tables.json","w+") as f:
                f.write(json.dumps(tables,indent=2))
    else:
        tables={}
    #time.sleep(0.2)
    os.remove("tables.lock")
    print("\rSyncing Tables...done     ")

def sync_totals(shift=None):
    ensure_dir("data/counts")
    tblf="data/counts/totals_"+shift
    print("\rSyncing Product Totals...",end="")
    sys.stdout.flush()
    global totals
    if os.path.isfile(tblf+".lock"):
        print("\rSyncing Product Totals, Waiting...",end="")
        sys.stdout.flush()
        while True:
            if not os.path.isfile(tblf+".lock"):
                break
            time.sleep(0.1)
    open(tblf+".lock",'a').close()
    if os.path.isfile(tblf+".json"):
        with open(tblf+".json") as f:
            totals_new=json.loads(f.read())
            totals_new.update(totals)
            totals=totals_new
    else:
        totals={}
    with open(tblf+".json","w+") as f:
        f.write(json.dumps(totals,indent=2))
        f.flush()
    #time.sleep(0.2)
    os.remove(tblf+".lock")
    print("\rSyncing Product Totals...done     ")

notify={}
def sync_notify():
    global notify
    tblf="nofity"
    print("\rSyncing Notifications...",end="")
    sys.stdout.flush()
    global totals
    if os.path.isfile(tblf+".lock"):
        print("\rSyncing Notifications, Waiting...",end="")
        sys.stdout.flush()
        while True:
            if not os.path.isfile(tblf+".lock"):
                break
            time.sleep(0.1)
    open(tblf+".lock",'a').close()
    if os.path.isfile("data/notify.json"):
        with open("data/notify.json") as f:
            notify_new=json.loads(f.read())
            notify_new.update(notify)
            notify=notify_new
    else:
        notify={}
    with open("data/notify.json","w+") as f:
        f.write(json.dumps(notify,indent=2))
        f.flush()
    #time.sleep(0.2)
    os.remove(tblf+".lock")
    print("\rSyncing Notifications...done     ")


def read_users():
    global users
    global user
    if os.path.isfile("data/users.json"):
        with open("data/users.json") as f:
            users=json.loads(f.read())

def write_users():
    global users
    with open("data/users.json","w+") as f:
        f.write(json.dumps(users,indent=2))
        f.flush()

def read_userdat(usr=None):
    global userdat
    global user
    if usr is None:
        if os.path.isfile("data/"+user+"/user.json"):
            with open("data/"+user+"/user.json") as f:
                userdat=json.loads(f.read())
                return True
    else:
        if os.path.isfile("data/"+usr+"/user.json"):
            with open("data/"+usr+"/user.json") as f:
                return json.loads(f.read())
    return False

def write_userdat(usr=None,altusrdat=None):
    global userdat
    global user
    if usr is None:
        ensure_dir("data/"+user)
        with open("data/"+user+"/user.json","w+") as f:
            f.write(json.dumps(userdat,indent=2))
            f.flush()
    else:
        ensure_dir("data/"+usr)
        with open("data/"+usr+"/user.json","w+") as f:
            f.write(json.dumps(altusrdat,indent=2))
            f.flush()

def read_useract(usr=None):
    global useract
    global user
    if usr is None:
        if os.path.isfile("data/"+user+"/activity.json"):
            with open("data/"+user+"/activity.json") as f:
                useract=json.loads(f.read())
                return True
    else:
        if os.path.isfile("data/"+usr+"/user.json"):
            with open("data/"+usr+"/user.json") as f:
                return json.loads(f.read())
    return False

def write_useract(usr=None,altusract=None):
    global useract
    global user
    if usr is None:
        ensure_dir("data/"+user)
        with open("data/"+user+"/activity.json","w+") as f:
            f.write(json.dumps(useract,indent=2))
            f.flush()
    else:
        ensure_dir("data/"+usr)
        with open("data/"+usr+"/activity.json","w+") as f:
            f.write(json.dumps(altusract,indent=2))
            f.flush()


def read_usertbl():
    global usertbl
    if os.path.isfile("data/"+user+"/counts/"+date+".json"):
        with open("data/"+user+"/counts/"+date+".json") as f:
            usertbl=json.loads(f.read())
    else:
        usertbl={}

def write_usertbl():
    global usertbl
    ensure_dir("data/"+user)
    ensure_dir("data/"+user+"/counts")
    with open("data/"+user+"/counts/"+date+".json","w+") as f:
        f.write(json.dumps(usertbl,indent=2))
        f.flush()

def sort_tables():
    global tables
    tables=DictSubSortNat(**tables)

def sort_usertables():
    global usertbl
    # print(user)
    # print(usertables)
    # time.sleep(5)
    # usertables=DictSubSortNat(**usertables)

def validate_input(inp,numeric=False):
    if numeric:
        if not inp.isnumeric():
            print("Input must be a Number")
            time.sleep(2)
            return True
    else:
        if not inp.isalnum():
            print("Input must be Alphanumeric")
            time.sleep(2)
            return True
        if len(inp)>4:
            print("Input too long")
            time.sleep(2)
            return True
    return False

def ensure_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def add_count(inp,bin=None,stable=None):
    global usertbl
    global table
    global prod
    if table=='383':
        bin="NoBin"
    if '*' in inp[1:]:
        spl=inp[1:].split('*')
        if validate_input(spl[0],True) or validate_input(spl[1],True):
            return False
        if stable is not None:
            set=False
            if bin is not None:
                if not bin in usertbl[table][stable]['polist'][prod]['ovf']:
                    usertbl[table][stable]['polist'][prod]['ovf'][bin]=[]
                if len(usertbl[table][stable]['polist'][prod]['ovf'][bin]) > 0:
                    for i,c in enumerate(usertbl[table][stable]['polist'][prod]['ovf'][bin]):
                        if '*' in c:
                            splc=c.split('*')
                            if splc[0]==spl[0]:
                                usertbl[table][stable]['polist'][prod]['ovf'][bin][i]=splc[0]+"*"+str(int(splc[1])+int(spl[1]))
                                set=True
                                break
            else:
                if len(usertbl[table][stable]['polist'][prod]['counts']) > 0:
                    for i,c in enumerate(usertbl[table][stable]['polist'][prod]['counts']):
                        if '*' in c:
                            splc=c.split('*')
                            if splc[0]==spl[0]:
                                usertbl[table][stable]['polist'][prod]['counts'][i]=splc[0]+"*"+str(int(splc[1])+int(spl[1]))
                                set=True
                                break
            if not set:
                if bin is not None:
                    usertbl[table][stable]['polist'][prod]['ovf'][bin].append(spl[0]+"*"+spl[1])
                else:
                    usertbl[table][stable]['polist'][prod]['counts'].append(spl[0]+"*"+spl[1])
            write_usertbl()
        else:
            tprod=prod
            if rev is not None:
                tprod=prod+'-'+rev
            set=False
            if bin is not None:
                if not bin in usertbl[table]['polist'][tprod]['ovf']:
                    usertbl[table]['polist'][tprod]['ovf'][bin]=[]
                if len(usertbl[table]['polist'][tprod]['ovf'][bin]) > 0:
                    for i,c in enumerate(usertbl[table]['polist'][tprod]['ovf'][bin]):
                        if '*' in c:
                            splc=c.split('*')
                            if splc[0]==spl[0]:
                                usertbl[table]['polist'][tprod]['ovf'][bin][i]=splc[0]+"*"+str(int(splc[1])+int(spl[1]))
                                set=True
                                break
                        elif c==spl[0]:
                            usertbl[table]['polist'][tprod]['ovf'][bin][i]=spl[0]+"*"+str(int(spl[1])+1)
                            set=True
                            break
            else:
                if not 'bin' in tables[table]['polist'][prod] and table!='383':
                    print("Must specify Bin for NoBin Products")
                    time.sleep(2)
                    return False
                elif tables[table]['polist'][prod]['bin']=='' and table!='383':
                    print("Must specify Bin for NoBin Products")
                    time.sleep(2)
                    return False

                if len(usertbl[table]['polist'][tprod]['counts']) > 0:
                    for i,c in enumerate(usertbl[table]['polist'][tprod]['counts']):
                        if '*' in c:
                            splc=c.split('*')
                            if splc[0]==spl[0]:
                                usertbl[table]['polist'][tprod]['counts'][i]=splc[0]+"*"+str(int(splc[1])+int(spl[1]))
                                set=True
                                break
                        elif c==spl[0]:
                            usertbl[table]['polist'][tprod]['counts'][i]=spl[0]+"*"+str(int(spl[1])+1)
                            set=True
                            break
            if not set:
                if bin is not None:
                    usertbl[table]['polist'][tprod]['ovf'][bin].append(spl[0]+"*"+spl[1])
                else:
                    usertbl[table]['polist'][tprod]['counts'].append(spl[0]+"*"+spl[1])
            write_usertbl()
    else:
        if validate_input(inp[1:],True):
            return False
        if stable is not None:
            set=False
            if bin is not None:
                if not bin in usertbl[table][stable]['polist'][prod]['ovf']:
                    usertbl[table][stable]['polist'][prod]['ovf'][bin]=[]
                if len(usertbl[table][stable]['polist'][prod]['ovf'][bin]) > 0:
                    for i,c in enumerate(usertbl[table][stable]['polist'][prod]['ovf'][bin]):
                        if '*' in c:
                            spl=c.split('*')
                            if spl[0]==inp[1:]:
                                usertbl[table][stable]['polist'][prod]['ovf'][bin][i]=spl[0]+"*"+str(int(spl[1])+1)
                                set=True
                                break
                        elif inp[1:]==c:
                            usertbl[table][stable]['polist'][prod]['ovf'][bin][i]=inp[1:]+"*2"
                            set=True
                            break
            else:
                if len(usertbl[table][stable]['polist'][prod]['counts']) > 0:
                    for i,c in enumerate(usertbl[table][stable]['polist'][prod]['counts']):
                        if '*' in c:
                            spl=c.split('*')
                            if spl[0]==inp[1:]:
                                usertbl[table][stable]['polist'][prod]['counts'][i]=spl[0]+"*"+str(int(spl[1])+1)
                                set=True
                                break
                        elif inp[1:]==c:
                            usertbl[table][stable]['polist'][prod]['counts'][i]=inp[1:]+"*2"
                            set=True
                            break
            if not set:
                if bin is not None:
                    usertbl[table][stable]['polist'][prod]['ovf'][bin].append(inp[1:])
                else:
                    usertbl[table][stable]['polist'][prod]['counts'].append(inp[1:])
            write_usertbl()
        else:
            tprod=prod
            if rev is not None:
                tprod=prod+'-'+rev
            set=False
            if bin is not None:
                if not bin in usertbl[table]['polist'][tprod]['ovf']:
                    usertbl[table]['polist'][tprod]['ovf'][bin]=[]
                if len(usertbl[table]['polist'][tprod]['ovf'][bin]) > 0:
                    for i,c in enumerate(usertbl[table]['polist'][tprod]['ovf'][bin]):
                        if '*' in c:
                            spl=c.split('*')
                            if spl[0]==inp[1:]:
                                usertbl[table]['polist'][tprod]['ovf'][bin][i]=spl[0]+"*"+str(int(spl[1])+1)
                                set=True
                                break
                        elif inp[1:]==c:
                            usertbl[table]['polist'][tprod]['ovf'][bin][i]=inp[1:]+"*2"
                            set=True
                            break
            else:
                if not 'bin' in tables[table]['polist'][prod]:
                    print("Must specify Bin for NoBin Products")
                    time.sleep(2)
                    return False
                elif tables[table]['polist'][prod]['bin']=='':
                    print("Must specify Bin for NoBin Products")
                    time.sleep(2)
                    return False
                if len(usertbl[table]['polist'][tprod]['counts']) > 0:
                    for i,c in enumerate(usertbl[table]['polist'][tprod]['counts']):
                        if '*' in c:
                            spl=c.split('*')
                            if spl[0]==inp[1:]:
                                usertbl[table]['polist'][tprod]['counts'][i]=spl[0]+"*"+str(int(spl[1])+1)
                                set=True
                                break
                        elif inp[1:]==c:
                            usertbl[table]['polist'][tprod]['counts'][i]=inp[1:]+"*2"
                            set=True
                            break
            if not set:
                if bin is not None:
                    usertbl[table]['polist'][tprod]['ovf'][bin].append(inp[1:])
                else:
                    usertbl[table]['polist'][tprod]['counts'].append(inp[1:])
            write_usertbl()

def rm_count(inp,bin=None,stable=None):
    global usertbl
    global table
    global prod
    if table=='383':
        bin="NoBin"
    if '*' in inp[1:]:
        spl=inp[1:].split('*')
        if validate_input(spl[0],True) or validate_input(spl[1],True):
            return False
        if stable is not None:
            set=False
            if not 'counts' in usertbl[table][stable]['polist'][prod]:
                print("No counts for this product")
                time.sleep(2)
                return
            if len(usertbl[table][stable]['polist'][prod]['counts']) > 0:
                for i,c in enumerate(usertbl[table][stable]['polist'][prod]['counts']):
                    if '*' in c:
                        splc=c.split('*')
                        if splc[0]==spl[0]:
                            usertbl[table][stable]['polist'][prod]['counts'][i]=splc[0]+"*"+str(int(splc[1])-int(spl[1]))
                            set=True
                            break
            if not set:
                usertbl[table][stable]['polist'][prod]['counts'].append(spl[0]+"*"+spl[1])
            write_usertbl()
        else:
            tprod=prod
            if rev is not None:
                tprod=prod+'-'+rev
            set=False
            if bin is not None:
                if not bin in usertbl[table]['polist'][tprod]['ovf']:
                    print("No counts for this bin")
                    time.sleep(2)
                    return
                if len(usertbl[table]['polist'][tprod]['ovf'][bin]) > 0:
                    for i,c in enumerate(usertbl[table]['polist'][tprod]['ovf'][bin]):
                        if '*' in c:
                            splc=c.split('*')
                            if splc[0]==spl[0]:
                                if int(splc[1])-int(spl[1])>1:
                                    usertbl[table]['polist'][tprod]['ovf'][bin][i]=splc[0]+"*"+str(int(splc[1])-int(spl[1]))
                                    set=True
                                elif int(splc[1])-int(spl[1])==1:
                                    usertbl[table]['polist'][tprod]['ovf'][bin][i]=splc[0]
                                    set=True
                                elif int(splc[1])-int(spl[1])==0:
                                    set=False
                                break
            else:
                if not 'counts' in usertbl[table]['polist'][tprod]:
                    print("No counts for this product")
                    time.sleep(2)
                    return False
                if len(usertbl[table]['polist'][tprod]['counts']) > 0:
                    for i,c in enumerate(usertbl[table]['polist'][tprod]['counts']):
                        if '*' in c:
                            splc=c.split('*')
                            if splc[0]==spl[0]:
                                if int(splc[1])-int(spl[1])>1:
                                    usertbl[table]['polist'][tprod]['counts'][i]=splc[0]+"*"+str(int(splc[1])-int(spl[1]))
                                    set=True
                                elif int(splc[1])-int(spl[1])==1:
                                    usertbl[table]['polist'][tprod]['counts'][i]=splc[0]
                                    set=True
                                elif int(splc[1])-int(spl[1])==0:
                                    set=False
                                break
            if not set:
                if bin is not None:
                    if spl[0]+"*"+spl[1] in usertbl[table]['polist'][tprod]['ovf'][bin]:
                        usertbl[table]['polist'][tprod]['ovf'][bin].remove(spl[0]+"*"+spl[1])
                    else:
                        print("Count(s) not in this bin")
                        time.sleep(2)
                        return False
                else:
                    if spl[0]+"*"+spl[1] in usertbl[table]['polist'][tprod]['counts']:
                        usertbl[table]['polist'][tprod]['counts'].remove(spl[0]+"*"+spl[1])
                    else:
                        print("Count(s) not in this bin")
                        time.sleep(2)
                        return False
            write_usertbl()
    else:
        if validate_input(inp[1:],True):
            return False
        if stable is not None:
            set=False
            if not 'counts' in usertbl[table][stable]['polist'][prod]:
                print("There are not counts for this product")
                time.sleep(2)
                return False
            if len(usertbl[table][stable]['polist'][prod]['counts']) > 0:
                for i,c in enumerate(usertbl[table][stable]['polist'][prod]['counts']):
                    if '*' in c:
                        spl=c.split('*')
                        if spl[0]==inp[1:]:
                            usertbl[table][stable]['polist'][prod]['counts'][i]=spl[0]+"*"+str(int(spl[1])-1)
                            set=True
                            break
                    elif inp[1:]==c:
                        if '*' in usertbl[table][stable]['polist'][prod]['counts'][i]:
                            spl=usertbl[table][stable]['polist'][prod]['counts'][i].split('*')
                            if spl[0]==inp[1:]:
                                if int(spl[1])-1>1:
                                    usertbl[table][stable]['polist'][prod]['counts'][i]=spl[0]+"*"+str(int(spl[1])-1)
                                elif int(spl[1])-1==1:
                                    usertbl[table][stable]['polist'][prod]['counts'][i]=spl[0]
                            set=True
                        break
            if not set:
                if inp[1:] in usertbl[table][stable]['polist'][prod]['counts']:
                    usertbl[table][stable]['polist'][prod]['counts'].remove(inp[1:])
            write_usertbl()
        else:
            tprod=prod
            if rev is not None:
                tprod=prod+'-'+rev
            set=False
            if bin is not None:
                if not 'ovf' in usertbl[table]['polist'][tprod]:
                    print("No counts in this bin")
                    time.sleep(2)
                    return False
                if not bin in usertbl[table]['polist'][tprod]['ovf']:
                    print("No counts in this bin")
                    time.sleep(2)
                    return False
                if len(usertbl[table]['polist'][tprod]['ovf'][bin]) > 0:
                    for i,c in enumerate(usertbl[table]['polist'][tprod]['ovf'][bin]):
                        if '*' in c:
                            spl=c.split('*')
                            if spl[0]==inp[1:]:
                                if int(spl[1])-1>1:
                                    usertbl[table]['polist'][tprod]['ovf'][bin][i]=spl[0]+"*"+str(int(spl[1])-1)
                                elif int(spl[1])-1==1:
                                    usertbl[table]['polist'][tprod]['ovf'][bin][i]=spl[0]
                                set=True
                                break
            else:
                if not 'counts' in tables[table]['polist'][prod]:
                    print("No counts for this product")
                    time.sleep(2)
                    return False
                if len(usertbl[table]['polist'][tprod]['counts']) > 0:
                    for i,c in enumerate(usertbl[table]['polist'][tprod]['counts']):
                        if '*' in c:
                            spl=c.split('*')
                            if spl[0]==inp[1:]:
                                if int(spl[1])-1>1:
                                    usertbl[table]['polist'][tprod]['counts'][i]=spl[0]+"*"+str(int(spl[1])-1)
                                elif int(spl[1])-1==1:
                                    usertbl[table]['polist'][tprod]['counts'][i]=spl[0]
                                set=True
                                break
            if not set:
                if bin is not None:
                    if inp[1:] in usertbl[table]['polist'][tprod]['ovf'][bin]:
                        usertbl[table]['polist'][tprod]['ovf'][bin].remove(inp[1:])
                else:
                    if inp[1:] in usertbl[table]['polist'][tprod]['counts']:
                        usertbl[table]['polist'][tprod]['counts'].remove(inp[1:])
            write_usertbl()

def start_session():
    sess_start=time.strftime('%Y%m%d%H%M%S',time.localtime())
    if os.path.isfile("data/notify.json"):
        print("\rStaring Session...",end="")
        if os.path.isfile("notify.lock"):
            print("\rStaring Session, Waiting...",end="")
            sys.stdout.flush()
            semisil=True
            while True:
                if not os.path.isfile("notify.lock"):
                    break
                time.sleep(0.1)
        open("notify.lock",'a').close()
        if os.path.isfile("data/notify.json"):
            with open("data/notify.json",'r') as f:
                notify=json.loads(f.read())
            if not 'clients' in notify:
                notify['clients']=[]
            if not session_id in notify['clients']:
                notify['clients'].append(session_id)
            if not session_alias in notify:
                notify[session_alias]={}
            if not session_id in notify[session_alias]:
                notify[session_alias][session_id]={}
            if not 'session_id_kill' in notify[session_alias][session_id]:
                notify[session_alias][session_id]['session_id_kill']=0
            if not 'session_id_prompt' in notify[session_alias][session_id]:
                notify[session_alias][session_id]['session_id_prompt']=''
            if not 'session_id_notify' in notify[session_alias][session_id]:
                notify[session_alias][session_id]['session_id_notify']=''
            if not 'session_id_close' in notify[session_alias][session_id]:
                notify[session_alias][session_id]['session_id_close']=0
            if not 'build' in notify[session_alias][session_id]:
                notify[session_alias][session_id]['build']=build
            if not 'times' in notify[session_alias][session_id]:
                notify[session_alias][session_id]['times']={'session_id_started':sess_start,'last_ack':sess_start}
                # notify[session_alias][session_id]['times']['last_ack']=time.strftime('%Y%m%d%H%M%S',time.localtime())
            with open("data/notify.json","w+") as f:
                f.write(json.dumps(notify,indent=2))
                f.flush()
            os.remove("notify.lock")
            print("\rStarting Session...done       ")

session_alias='fehtblmgr'
session_id=randomStringDigits()
start_session()
sys.excepthook = log_except_hook
signal.signal(signal.SIGINT, exp_silent_Handler)
signal.signal(signal.SIGPIPE, exp_silent_Handler)
signal.signal(signal.SIGHUP, exp_silent_Handler)
clear_screen()
users = {}
tables = {}
usertbl = {}
useract = {}
userdat = {}
totals = {}
colorama.init(autoreset=True)
ensure_dir('data')
if os.path.isfile("tblmgr.lock"):
    print('')
    print("Login has been disabled due to maintenance.")
    print("Please contact the system administrator")
    print('')
    print("Press any key to exit...")
    wait_key()
print('Starting Login...')
time.sleep(0.5)
clear_screen()
attempt=0
reset=False
today=time.strftime('%Y%m%d',time.localtime())
todaydt=datetime.fromtimestamp(mktime(time.localtime()))
date=today

user=None
while True:
    while True:
        read_users()
        print('')
        print("Warning: Unauthorized use of this software is prohibited.")
        if reset:
            print("Your password was reset, please login again.")
            reset=False
        if attempt==3:
            print("Too many attempts!")
            fail_login()
        if not login():
            attempt+=1
            print("Invalid login!")
        else:
            print('')
            break
        print('')
    attempt=0
    if 'reset_key' in userdat:
        if userdat['reset_key']:
            print("Password reset requested.")
            retry=False
            while True:
                newpw=stdiomask.getpass("New Password: ")
                if len(newpw)>0:
                    newkey=hash_password(newpw)
                    while True:
                        verpw=stdiomask.getpass("Verify Password: ")
                        if len(verpw)>0:
                            if verify_password(newkey,verpw):
                                retry=False
                                reset=True
                                userdat['key']=newkey
                                userdat['reset_key']=False
                                write_userdat()
                                break
                            else:
                                retry=True
                                print("Password mismatch!")
                                break
                    if not retry:
                        break
    needdetail=False
    if not 'detail' in userdat:
        userdat['detail']={'FirstName':'','LastName':'','Email':'','Phone':'','Shift':''}
    if not 'FirstName' in userdat['detail']:
        userdat['detail']['FirstName']=''
    if not 'LastName' in userdat['detail']:
        userdat['detail']['LastName']=''
    if not 'Email' in userdat['detail']:
        userdat['detail']['Email']=''
    if not 'Phone' in userdat['detail']:
        userdat['detail']['Phone']=''
    if not 'Shift' in userdat['detail']:
        userdat['detail']['Shift']=''
    if len(userdat['detail']['FirstName'])==0 or len(userdat['detail']['LastName'])==0 or len(userdat['detail']['Email'])==0 or len(userdat['detail']['Phone'])==0 or len(userdat['detail']['Shift'])==0:
        print("Some user details are missing:")
        if len(userdat['detail']['FirstName'])==0:
            while True:
                pmpt=input("First Name: ")
                if len(pmpt)>0:
                    break
            userdat['detail']['FirstName']=pmpt
        if len(userdat['detail']['LastName'])==0:
            while True:
                pmpt=input("Last Name: ")
                if len(pmpt)>0:
                    break
            userdat['detail']['Lastname']=pmpt
        if len(userdat['detail']['Email'])==0:
            while True:
                pmpt=input("Email: ")
                if len(pmpt)>0:
                    break
            userdat['detail']['Email']=pmpt
        if len(userdat['detail']['Phone'])==0:
            while True:
                pmpt=input("Phone: ")
                if len(pmpt)>0:
                    break
            userdat['detail']['Phone']=pmpt
        if len(userdat['detail']['Shift'])==0:
            while True:
                pmpt=input("Shift: ")
                if len(pmpt)>0:
                    break
            userdat['detail']['Shift']=pmpt
        write_userdat()
    if reset:
        user=None
        attempt=0
        clear_screen()
        continue
    print('')
    print("Please wait...")
    read_useract()
    read_usertbl()
    read_userdat()
    if not date in useract:
        useract[date]={}
    useract[date][time.strftime('%H%M%S',time.localtime())]="User logged in"
    userdat['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
    userdat['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
    write_useract()
    write_userdat()
    sync_tables()
    sync_notify()
    #sync_totals()
    time.sleep(0.5)
    clear_screen()
    if userdat['detail']['FirstName']!="" and userdat['detail']['LastName']!="":
        print('\x1b[0;30;47m'+userdat['detail']['FirstName']+' '+userdat['detail']['LastName']+'\x1b[0m',end=" ")
    print('\x1b[0;30;47m'+time.strftime('%Y.%m.%d',time.strptime(date, '%Y%m%d'))+'\x1b[0m')
    print("Welcome to Infinity.FehrerTblMgr!")
    print("    Type 'help' without quotes")
    print("      for a list of valid commands.")
    print('')

    while True:
        cmd = input(">").rstrip().lower()
        if cmd=="help":
            print('')
            print('[Help]')
            print('--Work tasks------------------------------------------------')
            print('mytables : Manage my tables. (Not yet Implemented)')
            print('--User Actions----------------------------------------------')
            print('help     : Displays this list of commands.')
            print('logout   : Logout.')
            print('exit     : Logout and exit.')
            print("rstpw    : Resets a User's password.")
            print("modusr   : Rename a User.")
            print("about    : Provides information about this software")
            print("           including licensing and usage.")
            if userdat['role'] in ['admin','supervisor','lead']:
                print('--'+userdat['role'].capitalize()+' Actions---------------------------------------------')
                print('exptotals : Exports Totals')
                print("buglog    : View Debug Logs")
                print("userlog   : View User Log.")
                # print("userwatch : Watch User's Activity.")
                # print('genasign  : Assigns each user a set of Product Tables at random. (Based on product count, Not yet Implemented)')
                print('gentmpl   : Generates PDFs for updated Product Tables.')
                # print('emltmpl   : Emails Product Tables for distribution. (Not yet Implemented)')
                print("rmusr     : Remove a User.")
                print("lsusr     : List Users.")
                print("addusr    : Add a new User.")
        elif cmd=="logout":
            if not date in useract:
                useract[date]={}
            useract[date][time.strftime('%H%M%S',time.localtime())]="User logged out"
            userdat['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
            write_useract()
            write_userdat()
            user=None
            attempt=0
            clear_screen()
            break
        elif cmd=='about':
            clear_screen()
            print("Alias       : Infinity.FehrerTbl")
            print("Version     : "+build)
            print("Description : Specifically designed to aid in inventory")
            print("              tracking for FS Fehrer Automotive GmbH.")
            print("Developer   : Christopher A Gordon")
            print("Contact     : Christopher_a_gordon@hotmail.com")
            print("Company     : InfinityResearchAndDevlopment (Unregistered)")
            print('')
            print("Software License:")
            print(LICENSE)
        elif cmd=="gentmpl":
            build_templ()
            pass
        elif cmd=="buglog":
            if not userdat['role'] in ['admin','supervisor','lead']:
                print("Unauthorized command!")
                time.sleep(2)
                continue
            if os.path.isfile("debuglog.json"):
                debuglog={}
                with open("debuglog.json") as f:
                    debuglog=json.loads(f.read())
                print("[Date]")
                for d in debuglog:
                    print(time.strftime('%Y.%m.%d',time.strptime(d, '%Y%m%d')))
                seld=None
                while True:
                    seld=input("Enter Date: ")
                    if len(seld)>0:
                        seld=time.strftime('%Y%m%d',time.strptime(seld, '%Y.%m.%d'))
                        if seld in debuglog:
                            break
                        print("Invalid Date")
                        time.sleep(2)
                        continue
                for t in debuglog[seld]:
                    print('['+time.strftime('%H:%M:%S',time.strptime(t,'%H%M%S'))+']')
                    print(debuglog[d][t])
                print('')
        # elif cmd=="userlog":
        #     if not userdat['role'] in ['admin','supervisor','lead']:
        #         print("Unauthorized command!")
        #         time.sleep(2)
        #         continue
        #     continue
        #     read_users()
        #     print('')
        #     print("[Users]")
        #     for u in users:
        #         print(u)
        #     print('')
        #     while True:
        #         selu=input("User: ")
        #         if len(selu)>0:
        #             if not selu in users:
        #                 print("Invalid User")
        #                 time.sleep(2)
        #                 continue

        elif cmd=="userwatch":
            if not userdat['role'] in ['admin','supervisor','lead']:
                print("Unauthorized command!")
                time.sleep(2)
                continue
            continue
        elif cmd=="exptotals":
            if not userdat['role'] in ['admin','supervisor','lead']:
                print("Unauthorized command!")
                time.sleep(2)
                continue
            expf=None
            print("Type abort to cancel")
            while True:
                pmpt=input("For what shift? [1/2/3]: ")
                if pmpt in ['1','2','3','abort']:
                    break
            sync_totals(pmpt)
            shift=None
            if pmpt=='1' or pmpt=='2' or pmpt=='3':
                expf="Cycles_"+pmpt
                if pmpt=='1':
                    expf+='st'
                    shift=pmpt+'st'
                elif pmpt=='2':
                    expf+='nd'
                    shift=pmpt+'nd'
                elif pmpt=='3':
                    expf+='rd'
                    shift=pmpt+'rd'
            else:
                expf="Cycles_"+pmpt
            if pmpt is not 'abort':
                print("\rFormatting Totals...",end="")
                sys.stdout.flush()
                # if not user in usertables:
                #     usertables[user]={}
                # if not date in usertables[user]:
                #     usertbl={}
                if not date in totals:
                    totals[date]={}
                tblz=OrderedDict(natsort.natsorted(totals[date].items()))
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
                        if 'counts' in tblz[p]:
                            for c in tblz[p]['counts']:
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
                        if 'ovf' in tblz[p]:
                            for b in tblz[p]['ovf']:
                                if len(tblz[p]['ovf'][b])>0:
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
                                    for c in tblz[p]['ovf'][b]:
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
                expf+='_'+stamp
                df = pd.DataFrame.from_dict(new_tots)

                writer = pd.ExcelWriter('export/'+expf+'.xlsx', engine='xlsxwriter')
                df.to_excel(writer, sheet_name='Cycle Counts',index=False)  # send df to writer
                workbook = writer.book
                #worksheet = workbook.add_worksheet('Cycle Counts')
                worksheet = writer.sheets['Cycle Counts']
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
                worksheet.conditional_format('A1:'+chr(ord('A')+len(new_tots)-1)+str(len(new_tots['PO'])+1),{'type': 'no_errors','format': formatBorders})
                worksheet.freeze_panes(1,0)
                worksheet.set_header("&L"+shift+" Shift Cycle Counts "+stamp+"&RPage:&P/&N",{'margin':0.3})
                worksheet.fit_to_pages(1,0)
                worksheet.set_margins(left=0.25,right=0.25,top=0.75,bottom=0.75)
                writer.save()
                print("\rGenerating Spreadsheet...done     ")
                sys.stdout.flush()
                print("Download Here: https://fehrertbl.infinitycommunicationsgateway.net/export/"+expf+".xlsx")
                # df.to_excel('csv/_'+expf+'.xlsx',date)
        elif cmd=="mytables":
            table=None
            stable=None
            prod=None
            bin=None
            rev=None
            # if userdat['role']=='user':
                # if not user in usertables:
                #     usertables[user]={}
                # if not date in usertables[user]:
                #     usertbl={}
            while True: # Print UI
                clear_screen()
                print("[Table]",end=' ')
                if userdat['detail']['FirstName']!="" and userdat['detail']['LastName']!="":
                    print('\x1b[0;30;47m'+userdat['detail']['FirstName']+' '+userdat['detail']['LastName']+'\x1b[0m',end=" ")
                print('\x1b[0;30;47m'+time.strftime('%Y.%m.%d',time.strptime(date, '%Y%m%d'))+'\x1b[0m')
                y=0
                for key in tables:
                    hasc=False
                    keystr=key
                    if hascounts(key):
                        hasc=True
                        keystr=str('\x1b[38;5;111m'+key+'\x1b[0m') # Red
                            # if len(keystr)==3:
                            #     print(' '+keystr.rjust(4),end='')
                    if y==7:
                        y=0
                        if key==table:
                            if hasc:
                                keystr=str('\x1b[48;5;111m\x1b[38;5;0m'+key+'\x1b[0m')
                            else:
                                keystr=str('\x1b[48;5;15m\x1b[38;5;0m'+key+'\x1b[0m')
                            # if len(keystr)==3:
                            #     print(' '+keystr.rjust(4))
                            # else:
                                print(keystr)
                        else:
                            # if len(keystr)==3:
                            #     print(' '+keystr.rjust(4))
                            # else:
                            print(keystr)
                    else:
                        if key==table:
                            if hasc:
                                keystr=str('\x1b[48;5;111m\x1b[38;5;0m'+key+'\x1b[0m')
                            else:
                                keystr=str('\x1b[48;5;15m\x1b[38;5;0m'+key+'\x1b[0m')
                            # if len(keystr)==3:
                            #     print(' '+keystr.rjust(4),end=' ')
                            # else:
                            print(keystr,end=' ')
                        else:
                            # if len(keystr)==3:
                            #     print(' '+keystr.rjust(4),end='')
                            # else:
                            print(keystr,end=' ')
                        y+=1
                    if key==list(tables.keys())[-1]:
                        print('')
                print('')
                if table is not None:
                    if 'polist' not in tables[table]:
                        print("[SubTable]")
                        y=0
                        for key in tables[table]:
                            if key==list(tables[table].keys())[-1]:
                                print('')
                            if key in ['times','type']:
                                continue
                            if y==7:
                                y=0
                                if key==stable:
                                    print('\x1b[0;30;47m'+key+'\x1b[0m'.rjust(4))
                                else:
                                    print(key.rjust(4))
                            else:
                                if key==stable:
                                    print('\x1b[0;30;47m'+key+'\x1b[0m'.rjust(4),end=" ")
                                else:
                                    print(key.rjust(4),end=" ")
                                y+=1
                        print('')
                        if stable is not None:
                            if len(tables[table][stable]['polist']) > 0:
                                print("[Product]")
                                y=0
                                for po in tables[table][stable]['polist']:
                                    if y==6:
                                        y=0
                                        if po==prod:
                                            print('\x1b[0;30;47m'+po+'\x1b[0m'.rjust(4))
                                        else:
                                            if table in usertbl:
                                                if stable in usertbl[table]:
                                                    if po in usertbl[table][stable]['polist']:
                                                        haso=False
                                                        if 'ovf' in usertbl[table][stable]['polist'][po]:
                                                            for b in usertbl[table][stable]['polist'][po]['ovf']:
                                                                if len(usertbl[table][stable]['polist'][po]['ovf'][b])>0:
                                                                    print('\x1b[1;34;40m'+po+'\x1b[0m'.rjust(4))
                                                                    haso=True
                                                                    break
                                                        if not haso:
                                                            if 'counts' in usertbl[table][stable]['polist'][po]:
                                                                if len(usertbl[table][stable]['polist'][po]['counts'])>0:
                                                                    print('\x1b[1;34;40m'+po+'\x1b[0m'.rjust(4))
                                                                else:
                                                                    print(po.rjust(4))
                                                    else:
                                                        print(po.rjust(4))
                                                else:
                                                    print(po.rjust(4))
                                            else:
                                                print(po.rjust(4))
                                    else:
                                        if po==prod:
                                            print('\x1b[0;30;47m'+po+'\x1b[0m'.rjust(4),end=" ")
                                        else:
                                            if table in usertbl:
                                                if stable in usertbl[table]:
                                                    if po in usertbl[table][stable]['polist']:
                                                        haso=False
                                                        if 'ovf' in usertbl[table][stable]['polist'][po]:
                                                            for b in usertbl[table][stable]['polist'][po]['ovf']:
                                                                if len(usertbl[table][stable]['polist'][po]['ovf'][b])>0:
                                                                    print('\x1b[1;34;40m'+po+'\x1b[0m'.rjust(4),end=" ")
                                                                    haso=True
                                                                    break
                                                        if not haso:
                                                            if 'counts' in usertbl[table][stable]['polist'][po]:
                                                                if len(usertbl[table][stable]['polist'][po]['counts'])>0:
                                                                    print('\x1b[1;34;40m'+po+'\x1b[0m'.rjust(4),end=" ")
                                                                else:
                                                                    print(po.rjust(4),end=" ")
                                                            else:
                                                                print(po.rjust(4),end=" ")
                                                    else:
                                                        print(po.rjust(4),end=" ")
                                                else:
                                                    print(po.rjust(4),end=" ")
                                            else:
                                                print(po.rjust(4),end=" ")
                                        y+=1
                                    if po==list(tables[table][stable]['polist'].keys())[-1]:
                                        print('')
                                print('')
                    else:
                        if len(tables[table]['polist']) > 0:
                            print("[Product]")
                            y=0
                            for po in tables[table]['polist']:
                                lastdt=datetime.fromtimestamp(mktime(time.strptime(tables[table]['polist'][po]['times']['accessed'],'%Y%m%d%H%M%S')))
                                tdelta=todaydt-lastdt
                                if 'rev' in tables[table]['polist'][po]:
                                    for r in tables[table]['polist'][po]['rev']:
                                        postr=str(po+'-'+r)
                                        if tdelta.days>=28:
                                            continue
                                        elif tdelta.days>21:
                                            postr=str('\x1b[38;5;203m'+postr+'\x1b[0m') # Red
                                        elif tdelta.days>7:
                                            postr=str('\x1b[38;5;185m'+postr+'\x1b[0m') # Yellow
                                        else:
                                            postr='\x1b[38;5;048m'+postr.rjust(8)+'\x1b[0m' # Green
                                        if y==6:
                                            y=0
                                            if hascounts(table,po+'-'+r):
                                                if po==prod and r==rev:
                                                    print(str('\x1b[48;5;111m\x1b[38;5;0m'+str(po+'-'+r).rjust(8)+'\x1b[0m')) # Red
                                                else:
                                                    print(str('\x1b[38;5;111m'+str(po+'-'+r).rjust(8)+'\x1b[0m')) # Red
                                            else:
                                                if po==prod and r==rev:
                                                    if tdelta.days>21:
                                                        print(str('\x1b[48;5;203m\x1b[38;5;0m'+str(po+'-'+r).rjust(8)+'\x1b[0m')) # Red
                                                    elif tdelta.days>7:
                                                        print(str('\x1b[48;5;185m\x1b[38;5;0m'+str(po+'-'+r).rjust(8)+'\x1b[0m')) # Yellow
                                                    else:
                                                        print(str('\x1b[48;5;048m\x1b[38;5;0m'+str(po+'-'+r).rjust(8)+'\x1b[0m')) # Green
                                                else:
                                                    print(postr) # Default
                                        else:
                                            if hascounts(table,po+'-'+r):
                                                if po==prod and r==rev:
                                                    print(str('\x1b[48;5;111m\x1b[38;5;0m'+str(po+'-'+r).rjust(8)+'\x1b[0m'),end=" ") # Red
                                                else:
                                                    print(str('\x1b[38;5;111m'+str(po+'-'+r).rjust(8)+'\x1b[0m'),end=" ") # Red
                                            else:
                                                if po==prod and r==rev:
                                                    if tdelta.days>21:
                                                        print(str('\x1b[48;5;203m\x1b[38;5;0m'+str(po+'-'+r).rjust(8)+'\x1b[0m'),end=" ") # Red
                                                    elif tdelta.days>7:
                                                        print(str('\x1b[48;5;185m\x1b[38;5;0m'+str(po+'-'+r).rjust(8)+'\x1b[0m'),end=" ") # Yellow
                                                    else:
                                                        print(str('\x1b[48;5;048m\x1b[38;5;0m'+str(po+'-'+r).rjust(8)+'\x1b[0m'),end=' ') # Yellow
                                                else:
                                                    print(postr,end=" ") # Green
                                            y+=1
                                        if po==list(tables[table]['polist'].keys())[-1]:
                                            print('')
                                else:
                                    postr=""
                                    postr=po+'-???'
                                    if tdelta.days>=28:
                                        continue
                                    elif tdelta.days>21:
                                        postr=str('\x1b[38;5;203m'+postr+'\x1b[0m') # Red
                                    elif tdelta.days>7:
                                        postr=str('\x1b[38;5;185m'+postr+'\x1b[0m') # Yellow
                                    else:
                                        postr='\x1b[38;5;048m'+postr.rjust(8)+'\x1b[0m' # Green
                                    if y==6:
                                        y=0
                                        if hascounts(table,po+'-???'):
                                            if po==prod and r==rev:
                                                print(str('\x1b[48;5;111m\x1b[38;5;0m'+po+'-???'.rjust(8)+'\x1b[0m')) # Red
                                            else:
                                                print(str('\x1b[38;5;111m'+po+'-???'.rjust(8)+'\x1b[0m')) # Red
                                        else:
                                            if po==prod and r==rev:
                                                if tdelta.days>21:
                                                    print(str('\x1b[48;5;203m\x1b[38;5;0m'+po+'-???'.rjust(8)+'\x1b[0m')) # Red
                                                elif tdelta.days>7:
                                                    print(str('\x1b[48;5;185m\x1b[38;5;0m'+po+'-???'.rjust(8)+'\x1b[0m')) # Yellow
                                                else:
                                                    print(str('\x1b[48;5;048m\x1b[38;5;0m'+postr.rjust(8)+'\x1b[0m')) # Yellow
                                            else:
                                                print(postr) # Default
                                    else:
                                        if hascounts(table,po+'-???'):
                                            if po==prod and r==rev:
                                                print(str('\x1b[48;5;111m\x1b[38;5;0m'+po+'-???'.rjust(8)+'\x1b[0m'),end=" ") # Red
                                            else:
                                                print(str('\x1b[38;5;111m'+po+'-???'.rjust(8)+'\x1b[0m'),end=" ") # Red
                                        else:
                                            if po==prod and r==rev:
                                                if tdelta.days>21:
                                                    print(str('\x1b[48;5;203m\x1b[38;5;0m'+po+'-???'.rjust(8)+'\x1b[0m'),end=" ") # Red
                                                elif tdelta.days>7:
                                                    print(str('\x1b[48;5;185m\x1b[38;5;0m'+po+'-???'.rjust(8)+'\x1b[0m'),end=" ") # Yellow
                                                else:
                                                    print(str('\x1b[48;5;048m\x1b[38;5;0m'+po+'-???'.rjust(8)+'\x1b[0m'),end=' ') # Yellow
                                            else:
                                                print(postr,end=" ") # Red
                                        y+=1
                                    if po==list(tables[table]['polist'].keys())[-1]:
                                        print('')
                            print('')
                if userdat['role']=="user":
                    # if table is not None and prod is not None:
                    #     total=0
                    #     counts=[]
                    #     if stable is not None:
                    #         counts=usertbl[table][stable]['polist'][prod]['counts']
                    #     else:
                    #         counts=usertbl[table]['polist'][prod]['counts']
                    #     if len(counts) > 0:
                    #         print("[Counts]")
                    #         for c in counts:
                    #             if '*' in c:
                    #                 spl=c.split('*')
                    #                 print(spl[0]+"(x"+spl[1]+')',end=' ')
                    #                 total+=int(spl[0])*int(spl[1])
                    #             else:
                    #                 print(c,end=' ')
                    #                 total+=int(c)
                    #             if c==list(counts)[-1]:
                    #                 print('')
                    #         print("  Total: "+str(total))
                    #         print('')
                    if table is not None and prod is not None:
                        total=0
                        counts=[]
                        tbin=None
                        dcount=None
                        tdelta=None
                        if stable is not None:
                            counts=usertbl[table][stable]['polist'][prod]['counts']
                            if "bin" in tables[table][stable]['polist'][prod]:
                                if tables[table][stable]['polist'][prod]["bin"] is not '':
                                    tbin=table[table][stable]['polist'][prod]["bin"]
                        else:
                            if rev is not None:
                                if prod+'-'+rev in usertbl[table]['polist']:
                                    if 'counts' in usertbl[table]['polist'][prod+'-'+rev]:
                                        counts=usertbl[table]['polist'][prod+'-'+rev]['counts']
                                if "bin" in tables[table]['polist'][prod]:
                                    if tables[table]['polist'][prod]["bin"] is not '':
                                        tbin=tables[table]['polist'][prod]["bin"]
                                if "counts" in tables[table]['polist'][prod]:
                                    if tables[table]['polist'][prod]["counts"] is not '':
                                        dcount=tables[table]['polist'][prod]["counts"]
                                lastdt=datetime.fromtimestamp(mktime(time.strptime(tables[table]['polist'][prod]['times']['accessed'],'%Y%m%d%H%M%S')))
                                tdelta=todaydt-lastdt
                        # Print Product Bins/Counts
                        print("[Counts]",end=' ')
                        if tbin is not None:
                            print('\x1b[0;30;47m'+format_bin(tbin)+'\x1b[0m',end=' ')
                        else:
                            print('\x1b[0;30;47mNoBin\x1b[0m',end=' ')
                        if dcount is not None:
                            if dcount==0:
                                print('\x1b[0;30;47mNoQuant\x1b[0m',end=' ')
                            else:
                                print('\x1b[0;30;47m'+str(dcount)+'\x1b[0m',end=' ')
                        if tdelta is not None:
                            if tdelta.days==0:
                                print('\x1b[0;30;47mToday\x1b[0m',end=' ')
                            elif tdelta.days==1:
                                print('\x1b[0;30;47mYesterday\x1b[0m',end=' ')
                            elif tdelta.days>1:
                                print('\x1b[0;30;47m'+str(tdelta.days)+' Days ago\x1b[0m',end=' ')
                        print('')
                        if len(counts) > 0:
                            if tbin is not None:
                                print(format_bin(tbin)+':',end=' ')
                            for c in counts:
                                if '*' in c:
                                    spl=c.split('*')
                                    print(spl[0]+"(x"+spl[1]+')',end=' ')
                                    total+=int(spl[0])*int(spl[1])
                                else:
                                    print(c,end=' ')
                                    total+=int(c)
                                if c==list(counts)[-1]:
                                    print('')
                        if 'ovf' in usertbl[table]['polist'][prod+'-'+rev]:
                            if len(usertbl[table]['polist'][prod+'-'+rev]['ovf'])>0:
                                for p in usertbl[table]['polist'][prod+'-'+rev]['ovf']:
                                    if len(usertbl[table]['polist'][prod+'-'+rev]['ovf'][p])>0:
                                        print(format_bin(p)+':',end=' ')
                                        for c in usertbl[table]['polist'][prod+'-'+rev]['ovf'][p]:
                                            if '*' in c:
                                                spl=c.split('*')
                                                print(spl[0]+"(x"+spl[1]+')',end=' ')
                                                total+=int(spl[0])*int(spl[1])
                                            else:
                                                print(c,end=' ')
                                                total+=int(c)
                                            if c==list(usertbl[table]['polist'][prod+'-'+rev]['ovf'][p])[-1]:
                                                print('')
                        if total>0:
                            print("  Total: "+str(total))
                            print('')
                inp=None
                while True:
                    inp=input(":")
                    if len(inp)>0:
                        break
                if inp=='return':
                    break
                if inp=='submit':
                    counts=0
                    if userdat['role']=='admin':
                        print("Admins cannot submit counts")
                        time.sleep(2)
                        continue
                    elif userdat['role']=='user':
                        consent=None
                        while True:
                            consent=input("Are you Sure? [yes/no]: ")
                            if len(consent)>0:
                                if consent=="yes":
                                    break
                                elif consent=="no":
                                    break
                        if consent=="no":
                            continue
                        shift=None
                        while True:
                            pmpt=input("For what shift? [1/2/3]: ")
                            if pmpt in ['1','2','3']:
                                break
                        shift=pmpt
                        sync_totals(shift)
                        if not date in totals:
                            totals[date]={}
                        stamp=time.strftime('%Y%m%d%H%M%S',time.localtime())
                        for t in usertbl:
                            if 'polist' in usertbl[t]:
                                if len(usertbl[t]['polist'])>0:
                                    for p in usertbl[t]['polist']:
                                        haso=False
                                        if 'ovf' in usertbl[t]['polist'][p]:
                                            for b in usertbl[t]['polist'][p]['ovf']:
                                                if len(usertbl[t]['polist'][p]['ovf'][b])>0:
                                                    haso=True
                                                    break
                                        if haso:
                                            if not t+p in totals[date]:
                                                totals[date][t+p]={}
                                            if not 'ovf' in totals[date][t+p]:
                                                totals[date][t+p]['ovf']={}
                                            for b in usertbl[t]['polist'][p]['ovf']:
                                                if len(usertbl[t]['polist'][p]['ovf'][b])>0:
                                                    for c in usertbl[t]['polist'][p]['ovf'][b]:
                                                        if not b in totals[date][t+p]['ovf']:
                                                            totals[date][t+p]['ovf'][b]=[]
                                                        if not c in totals[date][t+p]['ovf'][b]:
                                                            totals[date][t+p]['ovf'][b].append(c)
                                                            splp=p.split('-')
                                                            tables[t]['times']['accessed']=stamp
                                                            tables[t]['polist'][splp[0]]['times']['accessed']=stamp
                                                            counts+=1
                                        if 'counts' in usertbl[t]['polist'][p]:
                                            if len(usertbl[t]['polist'][p]['counts'])>0:
                                                if not t+p in totals[date]:
                                                    totals[date][t+p]={}# {'boxes':0,'partials':0,'total':0}
                                                if not 'counts' in totals[date][t+p]:
                                                    totals[date][t+p]['counts']=[]
                                                for c in usertbl[t]['polist'][p]['counts']:
                                                    if not c in totals[date][t+p]['counts']:
                                                        totals[date][t+p]['counts'].append(c)
                                                        splp=p.split('-')
                                                        tables[t]['times']['accessed']=stamp
                                                        tables[t]['polist'][splp[0]]['times']['accessed']=stamp
                                                        counts+=1
                            else:
                                for s in usertbl[t]:
                                    if s in ['type']:
                                        continue
                                    for p in usertbl[t][s]['polist']:
                                        if len(usertbl[t][s]['polist'][p]['counts'])>0:
                                            if not t+p+s in totals[date]:
                                                totals[date][t+p+s]=0 # {'boxes':0,'partials':0,'total':0}
                                            total=0
                                            for c in usertbl[t][s]['polist'][p]['counts']:
                                                if '*' in c:
                                                    spl=c.split('*')
                                                    total+=int(spl[0])*int(spl[1])
                                                else:
                                                    total+=int(c)
                                            totals[date][t+p+s]=total
                                            tables[t]['times']['accessed']=stamp
                                            tables[t][s]['times']['accessed']=stamp
                                            tables[t][s]['polist'][p]['times']['accessed']=stamp
                                            counts+=1
                        if not date in useract:
                            useract[date]={}
                        useract[date][time.strftime('%H%M%S',time.localtime())]="Submitted "+str(counts)+" counts"
                        userdat['times']['modified']=stamp
                        for rcvr in notify:
                            if rcvr=='clients':
                                continue
                            for ses in notify[rcvr]:
                                if 'refresh_counts' in notify[rcvr][ses]:
                                    notify[rcvr][ses]['refresh_counts']=1
                        write_useract()
                        write_userdat()
                        sync_totals(shift)
                        sync_tables()
                        sync_notify()
                        continue
                if inp=='help':
                    clear_screen()
                    print("[Help]")
                    print("Note: This is a quick rundown on how to use MyTables.")
                    print("  First off Data entry is performed by entering commands.")
                    print('  Next, we will go over some simple commands')
                    print('')
                    print('Press any key for next page...')
                    wait_key()
                    clear_screen()
                    # print(" Note: Anything in brackets [] are optional.")
                    print("[Basic Commands]")
                    print("Note: Below are some basic commands, they are used for")
                    print("  perforing various actions.")
                    print('')
                    print("help   : This tutorial")
                    print("submit : Submits all product counts")
                    print("return : Returns to main screen")
                    print("-all   : Removes all counts from Product")
                    print('')
                    print('Press any key for next page...')
                    wait_key()
                    clear_screen()
                    print("[Data Entry Basics]")
                    print("Note: Below, you can see the syntax of how to manage Data Entry.")
                    print('')
                    print("[Switching Tables]")
                    print(" /Table[.SubTable]          : Switch to Table/Subtable")
                    print('')
                    print('[Table Switching Example]')
                    print("Note: SubTables are not common use anymore, nor are the 11XX tables.")
                    print('')
                    print(" /090        : Switches to the 090 Table")
                    print(" /1100       : Switches to the 1100 Table")
                    print(" /1100.9906  : Switch to the 9906 SubTable in the 1100 Table")
                    # print(" /-Table[.SubTable]         : Remove a Table/SubTable")
                    print('')
                    print('Press any key for next page...')
                    wait_key()
                    clear_screen()
                    print("[Data Entry Basics]")
                    print("Note: Below, you can see the syntax of how to manage Data Entry.")
                    print('')
                    print("[Switching Products]")
                    print(" ++Product-Revision  : Select/Add a Product Number")
                    print(" ++                  : Jump to next Product/Revision")
                    print('')
                    print('[Product Switching Example]')
                    print("Note: You must always select a Product /w Revision Number before you.")
                    print("Note: If a product is unlisted, it will be added, if you are unsure of")
                    print("  the Revision number, simply use ??? instead.")
                    print("  you can use the '++' command.")
                    print(" ++0780-000 : Selects Product 0780 with Revision 0")
                    print(" ++1263-006 : Selects Product 1263 with Revision 6")
                    print(" ++         : Jump to Next Product/Revision")
                    print('')
                    print('Press any key for next page...')
                    wait_key()
                    clear_screen()
                    print("[Data Entry Basics]")
                    print("Note: Below, you can see the syntax of how to manage Data Entry.")
                    print("Note: Below, you will see entries in brackets [], these parts of")
                    print("  of the command are optional.")
                    print('')
                    print("[Adding Counts]")
                    print(" +Quantity[*Multiplier]     : Add counts to the selected Product.")
                    print(" +Quantity,Bin[*Multiplier] : Add counts to the selected bin.")
                    print(" +Bin,Quantity[*Multiplier] : Works in reverse.")
                    print('')
                    print("[Adding Counts Example]")
                    print(" +250         : Adds 250 to the Product's default Bin.")
                    print(" +1700*6      : Adds 6 Boxes of 250 to the Product's default Bin.")
                    print(" +a5o,250     : Adds 250 of Product to the A-05-OVF bin.")
                    print(" +250,a5o     : Works in reverse as well.")
                    print(" +aa3o,1700*6 : Adds 6 Boxes of Product with Quantity of 1700 to")
                    print("                  the AA-03-OVF bin.")
                    print(" +d223o,20    : Adds 20 of Product to the D2-02-03-OF bin.")
                    print('')
                    print('Press any key for next page...')
                    wait_key()
                    clear_screen()
                    print("[Data Entry Basics]")
                    print("Note: Below, you can see the syntax of how to manage Data Entry.")
                    print("Note: When entering counts to the default bin locations or")
                    print("  very specific NoBin products, you must enter each count")
                    print("  separately. However, you you specify a bin location, you")
                    print("  may chain your counts together as follows...")
                    print('')
                    print("[Adding Counts Example 2]")
                    print(" +250,a5o,b5o,c5o,z1o      : Adds 250 to the following bins")
                    print(" +250,a5o*10,b5o,c5o*2,z1o : Works in a similar manner, but")
                    print("                               by adding 10 boxes of 250 to")
                    print("                               A-05-OVF, and 2 to C-05-OVF.")
                    print(" +d251o,50*13,33,13,21     : This works in reverse as well..")
                    print("                               allowing you to enter multiple")
                    print("                               counts into the D2-02-5-1 bin.")
                    print('')
                    print('Press any key for next page...')
                    wait_key()
                    clear_screen()
                    print("[Data Entry Basics]")
                    print("Note: Below, you can see the syntax of how to manage Data Entry.")
                    print("Note: The act of removing counts works exactly the same way...")
                    print("  except your using a hyphen '-' instead of a plus sign '+'")
                    print('')
                    print("[Removing Counts]")
                    print(" -Bin,Quantity[*Multiplier] : Removes Quantity from Bin")
                    print(" -Quantity,Bin[*Multiplier] : Same as above")
                    print(" -Quantity[*Multiplier]     : Removes Quantity from Default Bin")
                    print('')
                    print('Press any key exit this tutorial...')
                    wait_key()
                    continue
                if inp[0]=='/':
                    if '.' in inp:
                        spl=inp[1:].split('.')
                        if inp[1]=='-':
                            spl=inp[2:].split('.')
                            if validate_input(spl[0]) or validate_input(spl[1]):
                                continue
                            time.sleep(1)
                            if userdat['role']=='admin':
                                if spl[0] not in tables:
                                    print("Table not found")
                                    time.sleep(2)
                                    continue
                                if spl[1] not in tables[spl[0]]:
                                    print("SubTable not found")
                                    time.sleep(2)
                                    continue
                                else:
                                    tables[spl[0]].pop(spl[1],None)
                                    tables[spl[0]]['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                                    if stable==spl[1]:
                                        stable=None
                                        prod=None
                                    sync_tables(push=True)
                            elif userdat['role']=='user':
                                if spl[0] not in usertbl:
                                    print("Table not found")
                                    time.sleep(2)
                                    continue
                                if spl[1] not in usertbl[spl[0]]:
                                    print("SubTable not found")
                                    time.sleep(2)
                                    continue
                                else:
                                    usertbl[spl[0]].pop(spl[1],None)
                                    # usertbl[spl[0]][spl[1]]['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                                write_usertbl()
                            if stable==spl[1]:
                                stable=None
                                prod=None
                        else:
                            if validate_input(spl[0]) or validate_input(spl[1]):
                                continue
                            if not spl[0] in tables:
                                tables[spl[0]]={}
                                tables[spl[0]]['type']='table'
                                tables[spl[0]]['times']={'created':time.strftime('%Y%m%d%H%M%S',time.localtime()),'modified':time.strftime('%Y%m%d%H%M%S',time.localtime()),'accessed':time.strftime('%Y%m%d%H%M%S',time.localtime())}
                                sort_tables()
                            if not spl[1] in tables[spl[0]]:
                                tables[spl[0]]['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                                tables[spl[0]][spl[1]]={}
                                tables[spl[0]][spl[1]]['type']='subtable'
                                tables[spl[0]][spl[1]]['times']={'created':time.strftime('%Y%m%d%H%M%S',time.localtime()),'modified':time.strftime('%Y%m%d%H%M%S',time.localtime()),'accessed':time.strftime('%Y%m%d%H%M%S',time.localtime())}
                                tables[spl[0]][spl[1]]['polist']={}
                                sort_tables()
                            if userdat['role']=='user':
                                if not spl[0] in usertbl:
                                    usertbl[spl[0]]={}
                                    usertbl[spl[0]]['type']='table'
                                if not spl[1] in usertbl[spl[0]]:
                                    usertbl[spl[0]][spl[1]]={}
                                    usertbl[spl[0]][spl[1]]['type']='subtable'
                                    usertbl[spl[0]][spl[1]]['polist']={}
                                sort_usertables()
                            table=spl[0]
                            stable=spl[1]
                            prod=None
                            # tables[table]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                            # tables[table][stable]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                            sync_tables()
                            if userdat['role']=='user':
                                write_usertbl()
                    else:
                        if inp[1]=='-':
                            if validate_input(inp[2:]):
                                continue
                            if userdat['role']=='admin':
                                if inp[2:] not in tables:
                                    print("Table not found")
                                    time.sleep(2)
                                    continue
                                tables.pop(inp[2:],None)
                                sync_tables()
                            elif userdat['role']=='user':
                                if inp[2:] not in usertbl:
                                    print("Table not found")
                                    time.sleep(2)
                                    continue
                                usertbl.pop(inp[2:],None)
                                write_usertbl()
                            if table==inp[2:]:
                                table=None
                                stable=None
                                prod=None
                        else:
                            if validate_input(inp[1:]):
                                continue
                            if not inp[1:] in tables:
                                tables[inp[1:]]={}
                                tables[inp[1:]]['type']='table'
                                tables[inp[1:]]['times']={'created':time.strftime('%Y%m%d%H%M%S',time.localtime()),'modified':time.strftime('%Y%m%d%H%M%S',time.localtime()),'accessed':time.strftime('%Y%m%d%H%M%S',time.localtime())}
                                tables[inp[1:]]['polist']={}
                                sort_tables()
                            else:
                                if userdat['role']=='admin':
                                    stable=None
                            if userdat['role']=='user':
                                if not inp[1:] in usertbl:
                                    usertbl[inp[1:]]={}
                                    usertbl[inp[1:]]['type']='table'
                                    usertbl[inp[1:]]['polist']={}
                                    sort_usertables()
                                else:
                                    stable=None
                            table=inp[1:]
                            stable=None
                            prod=None
                            # tables[table]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                            sync_tables()
                            if userdat['role']=='user':
                                write_usertbl()
                elif inp[0:2]=="--":
                    if validate_input(inp[2:]):
                        continue
                    if table is None:
                        print("Please select a Table")
                        time.sleep(2)
                        continue
                    if userdat['role'] in ['admin','supervisor','lead']:
                        if not 'polist' in tables[table]:
                            if stable is None:
                                print("Please select a SubTable")
                                time.sleep(2)
                                continue
                            if inp[2:] in tables[table][stable]['polist']:
                                tables[table]['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                                tables[table][stable]['polist'].pop(inp[2:],None)
                                tables[table][stable]['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                                if prod==inp:
                                    prod=None
                                sync_tables()
                            else:
                                print("Product not in SubTable")
                                time.sleep(2)
                                continue
                        else:
                            if inp[2:] in tables[table]['polist']:
                                tables[table]['polist'].pop(inp[2:],None)
                                tables[table]['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                                sync_tables()
                                if prod==inp:
                                    prod=None
                            else:
                                print("Product not in Table")
                                time.sleep(2)
                                continue
                    elif userdat['role']=='user':
                        if not 'polist' in usertbl[table]:
                            if stable is None:
                                print("Please select a SubTable")
                                time.sleep(2)
                                continue
                            if inp[2:] in usertbl[table][stable]['polist']:
                                usertbl[table][stable]['polist'].pop(inp[2:],None)
                                write_usertbl()
                                if prod==inp:
                                    prod=None
                            else:
                                print("Product not in SubTable")
                                time.sleep(2)
                            continue
                        else:
                            if inp[2:] in usertbl[table]['polist']:
                                usertbl[table]['polist'].pop(inp[2:],None)
                                write_usertbl()
                                if prod==inp:
                                    prod=None
                            else:
                                print("Product not in Table")
                                time.sleep(2)
                                continue
                elif inp[0:2]=='++':
                    if table is not None:
                        if userdat['role']=='admin':
                            if '-' in inp[2:]:
                                # this is indicating a rev
                                spl=inp[2:].split('-')
                                rev=spl[1].lower()
                                inp='+'+spl[0]
                            else:
                                rev=None
                            if validate_input(inp[2:]):
                                continue
                            if not 'polist' in tables[table]:
                                if stable is None:
                                    print("Please select a SubTable")
                                    time.sleep(2)
                                    continue
                                if inp[2:] not in tables[table][stable]['polist']:
                                    print(inp)
                                    time.sleep(2)
                                    tables[table]['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                                    tables[table][stable]['polist'][inp[2:]]={}
                                    tables[table][stable]['polist'][inp[2:]]['times']={'created':time.strftime('%Y%m%d%H%M%S',time.localtime()),'modified':time.strftime('%Y%m%d%H%M%S',time.localtime()),'accessed':time.strftime('%Y%m%d%H%M%S',time.localtime())}
                                    tables[table][stable]['polist'][inp[2:]]['counts']=0
                                    tables[table][stable]['polist'][inp[2:]]['desc']=""
                                    tables[table][stable]['polist'][inp[2:]]['bin']=""
                                    sort_tables()
                                # tables[table]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                                # tables[table][stable]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                                # tables[table][stable]['polist'][inp[2:]]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                                #tables[table]['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                                prod=inp[2:]
                                sync_tables()
                            else:
                                if inp[2:] not in tables[table]['polist']:
                                    tables[table]['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                                    tables[table]['polist'][inp[2:]]={}
                                    tables[table]['polist'][inp[2:]]['times']={'created':time.strftime('%Y%m%d%H%M%S',time.localtime()),'modified':time.strftime('%Y%m%d%H%M%S',time.localtime()),'accessed':time.strftime('%Y%m%d%H%M%S',time.localtime())}
                                    tables[table]['polist'][inp[2:]]['counts']=0
                                    tables[table]['polist'][inp[2:]]['desc']=""
                                    tables[table]['polist'][inp[2:]]['bin']=""
                                    sort_tables()
                                    continue
                        elif userdat['role']=='user':
                            stamp=time.strftime('%Y%m%d%H%M%S',time.localtime())
                            if not 'polist' in usertbl[table] or not 'polist' in tables[table]:
                                if stable is None:
                                    print("Please select a SubTable")
                                    time.sleep(2)
                                    continue
                                cont=False
                                nrev=False
                                if inp[2:]=="":
                                    if prod is None:
                                        print("Please select a Product")
                                        time.sleep(2)
                                        continue
                                    for i,k in enumerate(list(tables[table][stable]['polist'].keys())):
                                        if k==prod:
                                            if len(list(tables[table][stable]['polist'].keys()))>i+1:
                                                inp="++"+list(tables[table][stable]['polist'].keys())[i+1]
                                            else:
                                                print("No more Products")
                                                time.sleep(2)
                                                cont=True
                                if cont:
                                    continue
                                if validate_input(inp[2:]):
                                    continue
                                if inp[2:] not in tables[table][stable]['polist']:
                                    time.sleep(2)
                                    tables[table]['times']['modified']=stamp
                                    tables[table][stable]['polist'][inp[2:]]={}
                                    tables[table][stable]['polist'][inp[2:]]['times']={'created':stamp,'modified':stamp,'accessed':stamp}
                                    tables[table][stable]['polist'][inp[2:]]['counts']=0
                                    tables[table][stable]['polist'][inp[2:]]['desc']=""
                                    tables[table][stable]['polist'][inp[2:]]['bin']=""
                                    sort_tables()
                                if inp[2:] not in usertbl[table][stable]['polist']:
                                    time.sleep(2)
                                    usertbl[table][stable]['polist'][inp[2:]]={}
                                    usertbl[table][stable]['polist'][inp[2:]]['counts']=[]
                                    usertbl[table][stable]['polist'][inp[2:]]['ovf']={}
                                    sort_usertables()
                                if not 'ovf' in usertbl[table][stable]['polist'][inp[2:]]:
                                    usertbl[table][stable]['polist'][inp[2:]]['ovf']={}
                                # tables[table]['times']['accessed']=stamp
                                # tables[table][stable]['times']['accessed']=stamp
                                # tables[table][stable]['polist'][inp[2:]]['times']['accessed']=stamp
                            else:
                                cont=False
                                if inp[2:]=="":
                                    if prod is None:
                                        print("Please select a Product")
                                        time.sleep(2)
                                        continue
                                    for i,k in enumerate(list(tables[table]['polist'].keys())):
                                        if k==prod:
                                            if 'rev' in tables[table]['polist'][k] and rev is not None:
                                                hasrev=False
                                                for j,l in enumerate(tables[table]['polist'][k]['rev']):
                                                    if l==rev:
                                                        if len(tables[table]['polist'][k]['rev'])>j+1:
                                                            inp="++"+prod+'-'+tables[table]['polist'][k]['rev'][j+1]
                                                            print("++"+prod+'-'+tables[table]['polist'][k]['rev'][j+1])
                                                            hasrev=True
                                                            break
                                                if not hasrev:
                                                    if len(list(tables[table]['polist'].keys()))>i+1:
                                                        tprod=list(tables[table]['polist'].keys())[i+1]
                                                        if 'rev' in tables[table]['polist'][tprod]:
                                                            inp="++"+tprod+'-'+tables[table]['polist'][tprod]['rev'][0]
                                                            rev=tables[table]['polist'][tprod]['rev'][0]
                                                        else:
                                                            inp="++"+tprod+'-???'
                                                            rev=None
                                                    else:
                                                        print("No more Products")
                                                        time.sleep(2)
                                                        cont=True
                                            else:
                                                if len(list(tables[table]['polist'].keys()))>i+1:
                                                    tprod=list(tables[table]['polist'].keys())[i+1]
                                                    if 'rev' in tables[table]['polist'][tprod]:
                                                            inp="++"+tprod+'-'+tables[table]['polist'][tprod]['rev'][0]
                                                            rev=tables[table]['polist'][tprod]['rev'][0]
                                                    else:
                                                        inp="++"+tprod+'-???'
                                                else:
                                                    print("No more Products")
                                                    time.sleep(2)
                                                    cont=True
                                if cont:
                                    continue
                                if '-' in inp[2:]:
                                    # this is indicating a rev
                                    spl=inp[2:].split('-')
                                    rev=spl[1]
                                    inp='++'+spl[0].upper()
                                else:
                                    print('Please include revision')
                                    time.sleep(2)
                                    continue
                                if validate_input(inp[2:]):
                                    continue
                                if inp[2:] not in tables[table]['polist']:
                                    tables[table]['times']['modified']=stamp
                                    tables[table]['polist'][inp[2:]]={}
                                    tables[table]['polist'][inp[2:]]['times']={'created':stamp,'modified':stamp,'accessed':stamp}
                                    tables[table]['polist'][inp[2:]]['counts']=0
                                    tables[table]['polist'][inp[2:]]['desc']=""
                                    tables[table]['polist'][inp[2:]]['bin']=""
                                    sort_tables()
                                if inp[2:]+'-'+rev not in usertbl[table]['polist']:
                                    usertbl[table]['polist'][inp[2:]+'-'+rev]={}
                                    usertbl[table]['polist'][inp[2:]+'-'+rev]['counts']=[]
                                    usertbl[table]['polist'][inp[2:]+'-'+rev]['ovf']={}
                                    # tables[table]['times']['accessed']=stamp
                                    # tables[table]['polist'][inp[2:]]['times']['accessed']=stamp
                                    sort_usertables()
                                if not 'ovf' in usertbl[table]['polist'][inp[2:]+'-'+rev]:
                                    usertbl[table]['polist'][inp[2:]+'-'+rev]['ovf']={}
                                if not 'rev' in tables[table]['polist'][inp[2:]]:
                                    tables[table]['polist'][inp[2:]]['rev']=[]
                                if not rev in tables[table]['polist'][inp[2:]]['rev']:
                                    tables[table]['polist'][inp[2:]]['rev'].append(rev)
                            prod=inp[2:]
                            sync_tables()
                            if userdat['role']=='user':
                                write_usertbl()
                    else:
                        print("Please select a Table")
                        time.sleep(2)
                        continue
                elif inp[0]=="+":
                    if userdat['role']=="admin":
                        print("Admins cannot modify product counts")
                        time.sleep(2)
                        continue
                    if table is None:
                        print("Please select a Table")
                        time.sleep(2)
                        continue
                    if not 'polist' in tables[table]:
                        if stable is None:
                            print("Please select a SubTable")
                            time.sleep(2)
                            continue
                    if prod is None:
                        print("Please select a Product")
                        time.sleep(2)
                        continue
                    if ',' in inp[1:]:
                        if ",," in inp:
                            inp=inp.replace(",,",",")
                        spl=inp[1:].split(',')
                        if validate_bin(spl[0]):
                            for i in range(1,len(spl)):
                                if '*' in spl[i]:
                                    spla=spl[i].split('*')
                                    if len(spla)>2:
                                        print("Too many multipliers")
                                        time.sleep(2)
                                        continue
                                    add_count('+'+spla[0]+'*'+spla[1],spl[0])
                                else:
                                    add_count('+'+spl[i],spl[0])
                        elif spl[0].isdigit():
                            for i in range(1,len(spl)):
                                if '*' in spl[i]:
                                    spla=spl[i].split('*')
                                    if len(spla)>2:
                                        print("Too many multipliers")
                                        time.sleep(2)
                                        continue
                                    if validate_bin(spla[0]) and spla[1].isdigit():
                                        add_count('+'+spl[0]+'*'+spla[1],spla[0])
                                    elif validate_bin(spla[1]) and spla[0].isdigit():
                                        add_count('+'+spl[0]+'*'+spla[0],spla[1])
                                    # elif spla[0].isdigit() and spla[1].isdigit():
                                    #     add_count('+'+spl[0]+'*'+spla[0],None)
                                    else:
                                        print("Invalid Count")
                                        time.sleep(2)
                                        continue
                                else:
                                    if not validate_bin(spl[i]):
                                        print("Invalid Count")
                                        time.sleep(2)
                                        continue
                                    add_count('+'+spl[0],spl[i])
                        else:
                            print("Invalid Count")
                            time.sleep(2)
                    else:
                        bin=None
                        if not add_count(inp,bin):
                            continue
                elif inp[0]=='-':
                    if userdat['role']=="admin":
                        print("Admins cannot modify product counts")
                        time.sleep(2)
                        continue
                    if table is None:
                        print("Please select a Table")
                        time.sleep(2)
                        continue
                    if not 'polist' in tables[table]:
                        if stable is None:
                            print("Please select a SubTable")
                            time.sleep(2)
                            continue
                    if prod is None:
                        print("Please select a Product")
                        time.sleep(2)
                        continue
                    if inp[1:]=='all':
                        # print(table+','+prod+','+rev)
                        if not table in usertbl:
                            print("Table has no counts")
                            time.sleep(2)
                            continue
                        if not stable is None:
                            if not stable in usertbl[table]:
                                print("SubTable has no counts")
                                time.sleep(2)
                                continue
                            if not prod in usertbl[table][stable]:
                                print("Product has no counts")
                                time.sleep(2)
                                continue
                            if not 'counts' in usertbl[table][stable][prod]:
                                print("Product has no counts")
                                time.sleep(2)
                                continue
                            if 'counts' in usertbl[table][stable][prod]:
                                if not len(usertbl[table][stable][prod]['counts']):
                                    print("Product has no counts")
                                    time.sleep(2)
                                    continue
                                usertbl[table][stable][prod]['counts']=[]
                        else:
                            if not 'polist' in usertbl[table]:
                                print("Table has no counts")
                                time.sleep(2)
                                continue
                            if not prod+'-'+rev in usertbl[table]['polist']:
                                print("Product has no counts")
                                time.sleep(2)
                                continue
                            if (not 'counts' in usertbl[table]['polist'][prod+'-'+rev]) and (not 'ovf' in usertbl[table]['polist'][prod+'-'+rev]):
                                print("Product has no counts")
                                time.sleep(2)
                                continue
                            hasc=False
                            if 'counts' in usertbl[table]['polist'][prod+'-'+rev]:
                                if len(usertbl[table]['polist'][prod+'-'+rev]['counts']):
                                    hasc=True
                                usertbl[table]['polist'][prod+'-'+rev]['counts']=[]
                            if 'ovf' in usertbl[table]['polist'][prod+'-'+rev]:
                                if len(usertbl[table]['polist'][prod+'-'+rev]['ovf']):
                                    hasc=True
                                usertbl[table]['polist'][prod+'-'+rev]['ovf']={}
                            if not hasc:
                                print("Product has no Counts")
                                time.sleep(2)
                                continue
                        continue
                    if ',' in inp[1:]:
                        if ",," in inp:
                            inp=inp.replace(",,",",")
                        spl=inp[1:].split(',')
                        if validate_bin(spl[0]):
                            for i in range(1,len(spl)):
                                if '*' in spl[i]:
                                    spla=spl[i].split('*')
                                    if len(spla)>2:
                                        print("Too many multipliers")
                                        time.sleep(2)
                                        continue
                                    rm_count('-'+spla[0]+'*'+spla[1],spl[0])
                                else:
                                    rm_count('-'+spl[i],spl[0])
                        elif spl[0].isdigit():
                            for i in range(1,len(spl)):
                                if '*' in spl[i]:
                                    spla=spl[i].split('*')
                                    if len(spla)>2:
                                        print("Too many multipliers")
                                        time.sleep(2)
                                        continue
                                    if validate_bin(spla[0]) and spla[1].isdigit():
                                        rm_count('-'+spl[0]+'*'+spla[1],spla[0])
                                    elif validate_bin(spla[1]) and spla[0].isdigit():
                                        rm_count('-'+spl[0]+'*'+spla[0],spla[1])
                                    # elif spla[0].isdigit() and spla[1].isdigit():
                                    #     add_count('+'+spl[0]+'*'+spla[0],None)
                                    else:
                                        print("Invalid Count")
                                        time.sleep(2)
                                        continue
                                else:
                                    if not validate_bin(spl[i]):
                                        print("Invalid Count")
                                        time.sleep(2)
                                        continue
                                    rm_count('-'+spl[0],spl[i])
                        else:
                            print("Invalid Count")
                            time.sleep(2)
                    else:
                        bin=None
                        if not rm_count(inp,bin):
                            continue
            # review    : Switch to table from another date
            # today     : Switch to today's table
            # return    : Return to main screen

            # if a table,subtable or product is added and does not exist in the global tables, it will be added.
            #     if a table,subtable or product is removed from user's profile, it will remain in the global table.
            #     if a table,subtable or product does not appear within 7 days in any profile it will be ommitted from all profiles until entered again.
            #     if a table,subtable or product does not appear within 30 days, it is removed from the global table.

            # Each profile will have it's own unique table for counts
            # Each profile's table will have a timestamp for creation and modification.
            # The profile's table cannot be modified after the end of the day
            # The user can view the tables from a prior date.
            # The global table with have a creation, and modification timestamp for each table, subtable, and product.
            # The admin can view trends of products over time.
        elif cmd=="lsusr":
            if not userdat['role']=="admin":
                print("Unauthorized command!")
                time.sleep(2)
                continue
            read_users()
            print('')
            print("[Users]")
            for u in users:
                print(u)
        elif cmd=="modusr":
            print('')
            if userdat['role'] in ['admin','supervisor','lead']:
                read_users()
                print("[Users]")
                for u in users:
                    print(u)
                print('')
                print("[RenameUser]")
                while True:
                    usr=input("User: ")
                    if len(usr)>0:
                        if usr=="!abort":
                            break;
                        if not usr in users:
                            print("User not found!")
                        else:
                            while True:
                                newusr=input("New Username: ")
                                if len(newusr)>0:
                                    if newusr=="!abort":
                                        break;
                                    if newusr in users:
                                        print("User already exists!")
                                    else:
                                        for i,u in enumerate(users):
                                            if u==usr:
                                                users[i]=newusr
                                        # users[newusr]=users.pop(usr)
                                        newuseract=read_useract(usr)
                                        newuserdat=read_userdat(usr)
                                        if not date in newuseract:
                                            newuseract[date]={}
                                        stamps=time.strftime('%H%M%S',time.localtime())
                                        newuseract[date][stamps]="Admin renamed user '"+usr+"' to '"+newusr+"'"
                                        newuserdat['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                                        if not date in useract:
                                            useract[date]={}
                                        useract[date][stamps]="Renamed user '"+usr+"' to '"+newusr+"'"
                                        write_useract(usr,newuseract)
                                        write_userdat(usr,newuserdat)
                                        write_users()
                                        os.rename('data/'+usr,'data/'+newusr)
                                        break
                                else:
                                    print("Invalid User.")
                            break
                    else:
                        print("Invalid User.")
            elif userdat['role']=="user":
                print("[RenameUser]")
                while True:
                    print("Type '!abort' without quotes to cancel.")
                    newusr=input("New Username: ")
                    if len(newusr)>0:
                        if newusr=="!abort":
                            break;
                        if newusr in users:
                            print("User already exists!")
                        else:
                            while True:
                                consent=input("Are you Sure? [yes/no]: ")
                                if len(consent)>0:
                                    if consent=="yes":
                                        for i,u in enumerate(users):
                                            if u==user:
                                                users[i]=newusr
                                        if not date in useract:
                                            useract[date]={}
                                        useract[date][time.strftime('%H%M%S',time.localtime())]="User '"+user+"' renamed to '"+newusr+"'"
                                        userdat['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                                        os.rename('data/'+user,'data/'+newusr)
                                        user=newusr
                                        write_users()
                                        write_useract()
                                        write_userdat()
                                        break
                                    elif consent=="no":
                                        break
                            break
                    else:
                        print("Invalid User.")
        elif cmd=="rmusr":
            if not userdat['role'] in ['admin','supervisor','lead']:
                print("Unauthorized command!")
                time.sleep(2)
                continue
            read_users()
            print('')
            print("[Users]")
            for u in users:
                print(u)
            print('')
            print("[RemoveUser]")
            while True:
                usr=input("User: ")
                if len(usr)>0:
                    if usr=="!abort":
                        break;
                    if not usr in users:
                        print("User not found!")
                    else:
                        users.remove(usr)
                        if not date in useract:
                            useract[date]={}
                        useract[date][time.strftime('%H%M%S',time.localtime())]="User '"+usr+"' removed"
                        write_useract()
                        shutil.rmtree('data/'+usr)
                        write_users()
                        break
                else:
                    print("Invalid User.")
        elif cmd=="rstpw":
            print('')
            if userdat['role'] in ['admin','supervisor','lead']:
                read_users()
                print("[Users]")
                for u in users:
                    print(u)
                print('')
                print("[ResetPassword]")
                while True:
                    usr=input("User: ")
                    if len(usr)>0:
                        if usr=="!abort":
                            break;
                        if not usr in users:
                            print("User not found!")
                        else:
                            tempkey=str(random.randint(1000,9999))
                            key=hash_password(tempkey)
                            altuserdat=read_userdat(usr)
                            altuseract=read_useract(usr)
                            altuserdat['key']=key
                            altuserdat['reset_key']=True
                            if not date in altuseract:
                                altuseract[date]={}
                            altuseract[date][time.strftime('%H%M%S',time.localtime())]="'"+user+"' reset user's password"
                            altuseract['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                            if not date in useract:
                                useract[date]={}
                            useract[date][time.strftime('%H%M%S',time.localtime())]="User '"+usr+"' password reset"
                            print("Temporary password is "+tempkey+'.')
                            write_userdat(usr,altuserdat)
                            write_useract(usr,altuseract)
                            write_useract()
                            break
                    else:
                        print("Invalid User.")
            elif userdat['role']=='user':
                print("[ResetPassword]")
                while True:
                    consent=input("Are you Sure? [yes/no]: ")
                    if len(consent)>0:
                        if consent=="yes":
                            tempkey=str(random.randint(1000,9999))
                            key=hash_password(tempkey)
                            userdat['key']=key
                            userdat['reset_key']=True
                            if not date in useract:
                                useract[date]={}
                            useract[date][time.strftime('%H%M%S',time.localtime())]="User password reset"
                            userdat['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                            print("Temporary password is "+tempkey+'.')
                            write_userdat()
                            write_useract()
                            break
                        elif consent=="no":
                            break
        elif cmd=="chdate":
            if not userdat['role'] in ['admin','supervisor','lead']:
                print("Unauthorized command!")
                time.sleep(2)
                continue
            pmpt=None
            while True:
                pmpt=input('Date:')
                if not len(pmpt):
                    print("Please enter date to continue")
                    continue
                if len(pmpt)==8 and pmpt.isdigit():
                    break
                else:
                    print("Invalid Date, Use format 'YYYYMMDD'")
            date=pmpt
        elif cmd=="addusr":
            if not userdat['role'] in ['admin','supervisor','lead']:
                print("Unauthorized command!")
                time.sleep(2)
                continue
            read_users()
            print('')
            print("[Users]")
            for u in users:
                print(u)
            print('')
            print("[AddUser]")
            while True:
                newusr=input("User: ")
                if len(newusr)>0:
                    if newusr=="!abort":
                        break;
                    if newusr in users:
                        print("User already exists!")
                    else:
                        tempkey=str(random.randint(1000,9999))
                        key=hash_password(tempkey)
                        if not date in useract:
                            useract[date]={}
                        useract[date][time.strftime('%H%M%S',time.localtime())]="Created user '"+newusr+"'"
                        altusrdat={'key': key,'reset_key': True,'role': 'user'}
                        stamp=time.strftime('%Y%m%d%H%M%S',time.localtime())
                        altusrdat['times']={'created':stamp,'modified':stamp,'accessed':stamp}
                        users.append(newusr)
                        print("Temporary pin is "+tempkey+'.')
                        write_users()
                        write_userdat(newusr,altusrdat)
                        write_useract(newusr,{})
                        break
                else:
                    print("Invalid User.")
        elif cmd=="exit":
            if not date in useract:
                useract[date]={}
            useract[date][time.strftime('%H%M%S',time.localtime())]="User logged out"
            userdat['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
            write_useract()
            write_userdat()
            exit()
        else:
            print("Invalid command.")
        print('')

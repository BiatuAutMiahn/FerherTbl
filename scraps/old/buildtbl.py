
import os.path
import json
from collections import OrderedDict

def genhtml(key,polist,page,pages,count):
    htmlhead='''
        <!DOCTYPE html>
        <html>
            <head>
                <link href="https://fonts.googleapis.com/css?family=Inconsolata" rel="stylesheet">
        		<style>
        			body {
        				width: 21cm;
        				/* height: 29.7cm; */
        				background-color: white;
        				font-family: 'Inconsolata', monospace;
        				font-size: 14pt;
        				font-weight:bold;
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
        				width:1.0569in;
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
    numfields='''
               <tbody>
                  <tr>
                     <td class="tbl-cell-hide">
                        <p class="tbl-cell-space">&nbsp;</p>
                     </td>
                     <td class="tbl-cell">
                        <p class="tbl-cell-space">&nbsp;</p>
                     </td>
                     <td class="tbl-cell">
                        <p class="tbl-cell-space">&nbsp;</p>
                     </td>
                     <td class="tbl-cell">
                        <p class="tbl-cell-space">&nbsp;</p>
                     </td>
                     <td class="tbl-cell">
                        <p class="tbl-cell-space">&nbsp;</p>
                     </td>
                     <td class="tbl-cell">
                        <p class="tbl-cell-space">&nbsp;</p>
                     </td>
                     <td class="tbl-cell">
                        <p class="tbl-cell-space">&nbsp;</p>
                     </td>
                     <td class="tbl-cell tbl-row-last">
                        <p class="tbl-cell-space">&nbsp;</p>
                     </td>
                  </tr>
                  <tr>
                     <td class="tbl-cell-hide">
                        <p class="tbl-cell-space">&nbsp;</p>
                     </td>
                     <td class="tbl-cell">
                        <p class="tbl-cell-space">&nbsp;</p>
                     </td>
                     <td class="tbl-cell">
                        <p class="tbl-cell-space">&nbsp;</p>
                     </td>
                     <td class="tbl-cell">
                        <p class="tbl-cell-space">&nbsp;</p>
                     </td>
                     <td class="tbl-cell">
                        <p class="tbl-cell-space">&nbsp;</p>
                     </td>
                     <td class="tbl-cell">
                        <p class="tbl-cell-space">&nbsp;</p>
                     </td>
                     <td class="tbl-cell">
                        <p class="tbl-cell-space">&nbsp;</p>
                     </td>
                     <td class="tbl-cell tbl-row-last">
                        <p class="tbl-cell-space">&nbsp;</p>
                     </td>
                  </tr>
                  <tr>
                     <td class="tbl-cell-hide">
                        <p class="tbl-cell-space">&nbsp;</p>
                     </td>
                     <td class="tbl-cell tbl-cell-foot">
                        <p class="tbl-cell-space">&nbsp;</p>
                     </td>
                     <td class="tbl-cell tbl-cell-foot">
                        <p class="tbl-cell-space">&nbsp;</p>
                     </td>
                     <td class="tbl-cell tbl-cell-foot">
                        <p class="tbl-cell-space">&nbsp;</p>
                     </td>
                     <td class="tbl-cell tbl-cell-foot">
                        <p class="tbl-cell-space">&nbsp;</p>
                     </td>
                     <td class="tbl-cell tbl-cell-foot">
                        <p class="tbl-cell-space">&nbsp;</p>
                     </td>
                     <td class="tbl-cell tbl-cell-foot">
                        <p class="tbl-cell-space">&nbsp;</p>
                     </td>
                     <td class="tbl-cell tbl-cell-foot tbl-row-last">
                        <p class="tbl-cell-space">&nbsp;</p>
                     </td>
                  </tr>
               </tbody>
    '''
    html=htmlhead
    if int(key) >= 1100 or pages>1:
        html+='''
            <div class="tbl-detail-wrap">
        '''
    else:
        html+='''
            <div class="tbl-detail-wrap hide">
        '''

    if int(key) >= 1100:
        html+='''
            <div class="tbl-detail eleven-ins">'''+key+'''</div>
        '''
    else:
        html+='''
            <div class="tbl-detail eleven-ins hide"></div>
        '''
    if int(pages)>1:
        html+='''
            <div class="tbl-detail page-ins">Page '''+str(page)+'''/'''+str(round(pages))+'''</div>
        </div>
        '''
    else:
        html+='''
            <div class="tbl-detail page-ins hide"></div>
        </div>
        '''
    html+='''
        <table class="tbl" border="0" cellspacing="0" cellpadding="0">
    '''
    start=(page-1)*49

    end=(pages-1)*49
    remains=count-end
    x=0
    y=0
    xi=0
    yi=0
                # if int(key) >= 1100:
                #     html+='''
                #         <tbody>
                #             <tr>
                #                 <td class="tbl-cell-root">
                #                     <p class="tbl-cell-space">'''+'0000'+'''</p>
                #                 </td>
                #     '''
                # else:
    if isinstance(polist, list):
        for i,v in enumerate(polist):
            if i < start:
                continue;
            if i>=(start+49):
                break
            if x==0:
                if i==start:
                    html+='''
                        <tbody>
                            <tr>
                                <td class="tbl-cell-root">
                                    <p class="tbl-cell-space">'''+key+'''</p>
                                </td>
                    '''
                else:
                    html+='''
                        <tbody>
                            <tr>
                                <td class="tbl-cell-hide">
                                    <p class="tbl-cell-space"></p>
                                </td>
                    '''
            if x==6:
            #     html+='''
            #              <td class="tbl-cell-head tbl-cell-fill">
            #                 <p class="tbl-cell-space">'''+v+'''</p>
            #              </td>
            #     '''
            # elif i == (start+(x*6)+5):
            #     x=0
                html+='''
                     <td class="tbl-cell-head tbl-row-last tbl-cell-fill">
                        <p class="tbl-cell-space">'''+v+'''</p>
                     </td>
                '''
                html+='''
                          </tr>
                       </tbody>
                '''
                html+=numfields
                y+=1
                x=0
                xi+=1
            else:
                html+='''
                         <td class="tbl-cell-head tbl-cell-fill">
                            <p class="tbl-cell-space">'''+v+'''</p>
                         </td>
                '''
                x+=1
                xi+=1
            print(str(xi)+'.'+str(start)+'.'+str(x)+','+str(y)+','+str(i)+': '+str(v));
        if xi<49:
            if x<7:
                for j in range(x,6):
                    html+='''
                             <td class="tbl-cell-head">
                                <p class="tbl-cell-space">&nbsp;</p>
                             </td>
                    '''
                    xi+=1
                html+='''
                     <td class="tbl-cell-head tbl-row-last">
                        <p class="tbl-cell-space">&nbsp</p>
                     </td>
                '''
                html+='''
                          </tr>
                       </tbody>
                '''
                html+=numfields
            x=0
            for j in range(int(xi/7),int(48/7)):
                html+='''
                    <tbody>
                        <tr>
                            <td class="tbl-cell-hide">
                                <p class="tbl-cell-space"></p>
                            </td>
                '''
                for k in range(0,6):
                    html+='''
                             <td class="tbl-cell-head">
                                <p class="tbl-cell-space">&nbsp;</p>
                             </td>
                    '''
                    xi+=1
                html+='''
                     <td class="tbl-cell-head tbl-row-last">
                        <p class="tbl-cell-space">&nbsp</p>
                     </td>
                '''
                html+='''
                          </tr>
                       </tbody>
                '''
                html+=numfields
    if isinstance(polist, dict):
        for i,v in enumerate(polist):
            print(v)
    html+='''
                    </table>
                </div>
            </body>
        </html>
    '''
    return html

def buildpages(tables):
    x=0
    y=0
    page=1
    for i,k in enumerate(tables):
        count=len(tables[k])
        pages=round(count/42)
        if count % 42 != 0:
            pages+=1
        html=''
        print(str(k)+','+str(pages))
        if pages>1:
            for p in range(1,pages):
                print(k+'.'+str(p)+".html")
                html=genhtml(k,tables[k],p,pages-1,count)
                with open('html/'+k+'.'+str(p)+".html", 'w') as outfile:
                    outfile.write(html)
                    outfile.close()
        else:
            html=genhtml(k,tables[k],1,1,count)
            with open('html/'+k+'.'+str(p)+".html", 'w') as outfile:
                outfile.write(html)
                outfile.close()

class DictSubSortLen(OrderedDict):
    def __init__(self, **kwargs):
        super(DictSubSortLen, self).__init__()
        for key, value in sorted(kwargs.items(), key=lambda x: len(x[1]), reverse=True):
            if isinstance(value, dict):
                self[key] = DictSubSortLen(**value)
            else:
                self[key] = value

tables=None
if os.path.isfile('tables.old.json'):
    with open('tables.old.json') as f:
        tables=json.loads(f.read())
tables=DictSubSortLen(**tables)
tables=OrderedDict(sorted(tables.items(), key=lambda t: len(t[0])))
# OrderedDict(sorted(tables.items(), key=lambda (k,v):len(v), reverse=True))
buildpages(tables)
# print(json.dumps(tables,indent=4))

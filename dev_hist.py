import signal
import atexit
import logging
import traceback
import subprocess
import platform
import os
import json
import readline
import time
import re
import sys
import random
import string
from collections import OrderedDict
import natsort

user_counts={}

users=None
tables=None
print('\x1b[48;5;0m\x1b[38;5;15m')
session_alias='fehcounts'
session_id=None
def pop_session():
    print("\rClosing Session...",end="")
    if os.path.isfile("notify.lock"):
        print("\rClosing Session, Waiting...",end="")
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
        if session_id in notify['clients']:
            notify['clients'].remove(session_id)
        if session_alias in notify:
            if session_id in notify[session_alias]:
                notify[session_alias].pop(session_id)
        with open("data/notify.json","w+") as f:
            f.write(json.dumps(notify,indent=2))
            f.flush()
        os.remove("notify.lock")
        print("\rClosing Session...Done       ")

def goodbye():
    pop_session()

def exp_silent_Handler(signal, frame):
    pop_session()
    exit(0)

def exp_ignore_Handler(signal, frame):
    pop_session()
    exit(0)

def log_except_hook(*exc_info):
    text = "".join(traceback.format_exception(*exc_info))
    stampt=time.strftime('%H%M%S',time.localtime())
    stampd=time.strftime('%Y%m%d',time.localtime())
    buglog={}
    if os.path.isfile("debuglog.json"):
        with open("debuglog.json") as f:
            buglog=json.loads(f.read())
    if not stampd in buglog:
        buglog[stampd]={}
    buglog[stampd][stampt]=text
    with open("debuglog.json","w+") as f:
        f.write(json.dumps(buglog,indent=2))
        f.flush()
    pop_session()
    print("An error has occurred, and has been reported.")
    print("Press any key to exit...")
    wait_key()


def randomStringDigits(stringLength=16):
    """Generate a random string of letters and digits """
    lettersAndDigits=string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))

def suggest(inp):
    tbl=inp[0:3]
    prod=None
    rev=None
    if len(inp)==9:
        prod=inp[3:6]
        rev=inp[6:9]
    elif len(inp)==7:
        prod=inp[3:7]
    elif len(inp)==6:
        prod=inp[3:6]
    elif len(inp)==11:
        prod=inp[3:7]
        rev=inp[8:11]
    if not '-' in inp:
        rev=None
    # print(tbl)
    # print(prod)
    # print(rev)
    find=[]
    for t in tables:
        if not 'polist' in tables[t]:
            continue
        for p in tables[t]['polist']:
            if not 'rev' in tables[t]['polist'][p]:
                if prod==p and tbl!=t:
                    if not t+p in find:
                        find.append(t+p)
            else:
                for r in tables[t]['polist'][p]['rev']:
                    if prod==p and tbl!=t:
                        if not t+p+'-'+r in find:
                            find.append(t+p+'-'+r)
                    elif t==tbl and p==prod and r!=rev:
                        if not t+p+'-'+r in find:
                            find.append(t+p+'-'+r)
    if len(find)>0:
        print('')
        print("Did you mean?")
        for s in find:
            print(' '+__builtins__.str(s))

def wait_key():
    result = None
    if os.name == 'nt':
        import msvcrt
        result = msvcrt.getch()
    else:
        import termios
        fd = sys.stdin.fileno()
        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)
        try:
            result = sys.stdin.read(1)
        except IOError:
            pass
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
    return result

def clear_screen():
    command = "clear"
    if platform.system().lower()=="nt":
        command = "cls"
    subprocess.call(command)
    return subprocess.call(command) == 0

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

def validate_bin(string):
    if re.match("^d[1-9]{3}o$",string) is not None:
        return True
    elif re.match("^d[1-9]{4}$",string) is not None:
        return True
    elif re.match("^[a-z][1-9]{2}$",string) is not None:
        return True
    elif re.match("^[a-z][1-9]o$",string) is not None:
        return True
    elif re.match("^aa[1-9]o$",string) is not None:
        return True
    elif string=="cfm":
        return True
    else:
        return False


def update():
    global tables
    global users
    global user_counts
    print("Updating Counts...",end='')
    sys.stdout.flush()
    if os.path.isfile("data/users.json"):
        with open("data/users.json") as f:
            users=json.loads(f.read())
    if os.path.isfile("tables.json"):
        with open("tables.json") as f:
            tables=json.loads(f.read())
    for u in users:
        if u in ["test","admin"]:
            continue
        if not u in user_counts:
            user_counts[u]={}
        if os.path.exists("data/"+u+"/counts"):
            for file in os.listdir("data/"+u+"/counts"):
                if file.endswith(".json"):
                    date=file.replace(".json","")
                    with open(os.path.join("data/"+u+"/counts",file)) as f:
                        if not date in user_counts[u]:
                            user_counts[u][date]={}
                        user_counts[u][date]=json.loads(f.read())
    print("\rUpdating Counts...Done")

notify={}
def sync_notify(rm_sess=0,reverse=False,ow=False,silent=False):
    global notify
    tblf="notify"
    semsil=False
    if not silent:
        print("\rSyncing Notifications...",end="")
        sys.stdout.flush()
    global totals
    if os.path.isfile(tblf+".lock"):
        print("\rSyncing Notifications, Waiting...",end="")
        sys.stdout.flush()
        semisil=True
        while True:
            if not os.path.isfile(tblf+".lock"):
                break
            time.sleep(0.1)
    open(tblf+".lock",'a').close()
    if os.path.isfile("data/notify.json"):
        if not ow:
            with open("data/notify.json") as f:
                if reverse:
                    notify_new=json.loads(f.read())
                    notify.update(notify_new)
                    # notify.update((k, notify_new[k]) for k in notify.keys() & notify_new.keys())
                else:
                    notify_new=json.loads(f.read())
                    notify_new.update(notify)
                    notify=notify_new
    else:
        notify={}
    if rm_sess:
        if session_id in notify['clients']:
            notify['clients'].remove(session_id)
            notify[session_alias].pop(session_id,None)
    with open("data/notify.json","w+") as f:
        f.write(json.dumps(notify,indent=2))
        f.flush()
    #time.sleep(0.2)
    os.remove(tblf+".lock")
    if semsil or not silent:
        print("\rSyncing Notifications...Done     ")


session_id=randomStringDigits()
build='20190716173515'
sess_start=time.strftime('%Y%m%d%H%M%S',time.localtime())
# print("Testing: ",end='')
# print(sys.argv)
clear_screen()
print("Welcome to Infinity.FehrerCounts (Build v"+time.strftime('%Y.%m.%d',time.strptime(build, '%Y%m%d%H%M%S'))+")")
print('')
update()
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
    if not 'refresh_counts' in notify[session_alias][session_id]:
        notify[session_alias][session_id]['refresh_counts']=0
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
    if notify[session_alias][session_id]['refresh_counts']:
        notify[session_alias][session_id]['refresh_counts']=0
        notify[session_alias][session_id]['times']['last_ack']=time.strftime('%Y%m%d%H%M%S',time.localtime())
    sync_notify()

signal.signal(signal.SIGINT, exp_silent_Handler)
signal.signal(signal.SIGHUP, exp_silent_Handler)
signal.signal(signal.SIGTERM, exp_silent_Handler)
signal.signal(signal.SIGPIPE, exp_silent_Handler)
sys.excepthook = log_except_hook
atexit.register(goodbye)
print('')
time.sleep(2)
while True:
    print("Please enter a Product Number including the revision number, or a bin location.")
    # print("Note: if there no results try revision '???' without quotes.")
    print("Note: You can also use the up arrow to show the last entered product.")
    print('')
    inp=input(':')
    if inp=='':
        clear_screen()
        continue
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
        if not 'refresh_counts' in notify[session_alias][session_id]:
            notify[session_alias][session_id]['refresh_counts']=0
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
        if notify[session_alias][session_id]['refresh_counts']==1:
            update()
            notify[session_alias][session_id]['refresh_counts']=0
            notify[session_alias][session_id]['times']['last_ack']=time.strftime('%Y%m%d%H%M%S',time.localtime())
            sync_notify()
            time.sleep(2)
    tbl=None
    rev=None
    prod=None
    results={}
    if not inp.replace('-','').isdigit():
        inp=inp.lower()
        inp=inp.replace('0','')
        inp=inp.replace('-','')
        inp=inp.replace('ovf','o')
        if inp=="cutfoam":
            inp='cfm'
    if validate_bin(inp):
        for u in user_counts:
            for d in user_counts[u]:
                for tbl in user_counts[u][d]:
                    if not 'polist' in user_counts[u][d][tbl]:
                        continue
                    for p in user_counts[u][d][tbl]['polist']:
                        if tbl in tables:
                            if 'polist' in tables[tbl]:
                                prod=''
                                if p[3:7].isdigit():
                                    prod=p[3:7]
                                else:
                                    prod=p[0:4]
                                if prod in tables[tbl]['polist']:
                                    tbin=False
                                    if 'bin' in tables[tbl]['polist'][prod]:
                                        if tables[tbl]['polist'][prod]['bin']!='':
                                            if tables[tbl]['polist'][prod]['bin']==inp:
                                                if 'counts' in user_counts[u][d][tbl]['polist'][p]:
                                                    for count in user_counts[u][d][tbl]['polist'][p]['counts']:
                                                        if not d in results:
                                                            results[d]={}
                                                        if not tbl+p in results[d]:
                                                            results[d][tbl+p]={}
                                                        if '*' in count:
                                                            spl=count.split('*')
                                                            if not tbl+spl[0] in results[d][tbl+p]:
                                                                results[d][tbl+p][spl[0]]=0
                                                            results[d][tbl+p][spl[0]]+=int(spl[1])
                                                        else:
                                                            if not count in results[d][tbl+p]:
                                                                results[d][tbl+p][count]=0
                                                            results[d][tbl+p][count]+=1
                                if 'ovf' in user_counts[u][d][tbl]['polist'][p]:
                                    for i,b in enumerate(user_counts[u][d][tbl]['polist'][p]['ovf']):
                                        str=''
                                        if b!=inp:
                                            continue
                                        if not d in results:
                                            results[d]={}
                                        if not tbl+p in results[d]:
                                            results[d][tbl+p]={}
                                        for count in user_counts[u][d][tbl]['polist'][p]['ovf'][b]:
                                            if '*' in count:
                                                spl=count.split('*')
                                                if not spl[0] in results[d][tbl+p]:
                                                    results[d][tbl+p][spl[0]]=0
                                                results[d][tbl+p][spl[0]]+=int(spl[1])
                                            else:
                                                if not count in results[d][tbl+p]:
                                                    results[d][tbl+p][count]=0
                                                results[d][tbl+p][count]+=1
        print(json.dumps(results,indent=4))
        clear_screen()
        print('\x1b[48;5;15m\x1b[38;5;0m'+' '+format_bin(inp)+' '+'\x1b[0m')
        results=DictSubSortNat(**results)
        dates=list(results.keys())
        for d in dates[-28:]:
            print('\x1b[48;5;0m\x1b[38;5;15m['+time.strftime('%Y.%m.%d',time.strptime(d,'%Y%m%d'))+']',end="\x1b[48;5;0m\n ")
            results[d]=DictSubSortNat(**results[d])
            for b in results[d]:
                print('\x1b[48;5;0m\x1b[38;5;111m'+format_bin(b)+'='+'\x1b[0m',end='')
                for c in results[d][b]:
                    print('\x1b[48;5;0m\x1b[38;5;048m'+c+"(x"+__builtins__.str(results[d][b][c])+')'+'\x1b[0m',end='\x1b[48;5;0m ')
            print('\x1b[48;5;0m')
            print('\x1b[48;5;0m')
        print('\x1b[48;5;0mPress any key to return')
        wait_key()
        clear_screen()
        continue
    else:
        if len(inp)<5:
            continue
        tbl=inp[0:3]
        if len(inp)==9:
            prod=inp[3:6]
            rev=inp[6:9]
        elif len(inp)==6:
            prod=inp[3:6]
            rev='???'
        elif len(inp)==11:
            if not '-' in inp:
                print("Please include revision number in search")
                time.sleep(2)
                continue
            prod=inp[3:7]
            rev=inp[8:11]
        # print(str(len(inp))+'.'+str(tbl)+','+str(prod)+','+str(rev))
        # time.sleep(2)
        # exit()
        for u in user_counts:
            for d in user_counts[u]:
                #only get last 4 dates
                if tbl not in user_counts[u][d]:
                    continue
                if not 'polist' in user_counts[u][d][tbl]:
                    continue
                if len(user_counts[u][d][tbl]['polist'])<1:
                    continue
                if rev is not None:
                    if not prod+'-'+rev in user_counts[u][d][tbl]['polist']:
                        if not prod in user_counts[u][d][tbl]['polist']:
                            continue
                else:
                    if not prod in user_counts[u][d][tbl]['polist']:
                        continue
                for p in user_counts[u][d][tbl]['polist']:
                    if rev is not None:
                        if p==prod+'-'+rev:
                            if 'counts' in user_counts[u][d][tbl]['polist'][p]:
                                if len(user_counts[u][d][tbl]['polist'][p]['counts'])>0:
                                    b="NoBin"
                                    if tbl in tables:
                                        if 'polist' in tables[tbl]:
                                            if prod in tables[tbl]['polist']:
                                                if 'bin' in tables[tbl]['polist'][prod]:
                                                    if 'bin'!='':
                                                        b=tables[tbl]['polist'][prod]['bin']
                                    for count in user_counts[u][d][tbl]['polist'][p]['counts']:
                                        if not d in results:
                                            results[d]={}
                                        if not b in results[d]:
                                            results[d][b]={}
                                        if '*' in count:
                                            spl=count.split('*')
                                            if not spl[0] in results[d][b]:
                                                results[d][b][spl[0]]=0
                                            results[d][b][spl[0]]+=int(spl[1])
                                        else:
                                            if not count in results[d][b]:
                                                results[d][b][count]=0
                                            results[d][b][count]+=1
                            if 'ovf' in user_counts[u][d][tbl]['polist'][p]:
                                str=''
                                for i,b in enumerate(user_counts[u][d][tbl]['polist'][p]['ovf']):
                                    for count in user_counts[u][d][tbl]['polist'][p]['ovf'][b]:
                                        if count=='':
                                            continue
                                        if not d in results:
                                            results[d]={}
                                        if not b in results[d]:
                                            results[d][b]={}
                                        if '*' in count:
                                            spl=count.split('*')
                                            if not spl[0] in results[d][b]:
                                                results[d][b][spl[0]]=0
                                            results[d][b][spl[0]]+=int(spl[1])
                                        else:
                                            if not count in results[d][b]:
                                                results[d][b][count]=0
                                            results[d][b][count]+=1
        results=DictSubSortNat(**results)
        if len(results)==0:
            print("No reuslts, Check revision number.")
            suggest(inp)
            print('')
            print('Press any key to return')
            wait_key()
            clear_screen()
            continue
        clear_screen()
        # print(results)
        if rev is not None:
            if (len(inp)==9 or len(inp)==6) and rev=="???":
                rev=''
            else:
                rev='-'+rev
        else:
            rev=''
        print('\x1b[48;5;15m\x1b[38;5;0m'+' '+__builtins__.str(tbl)+__builtins__.str(prod)+__builtins__.str(rev)+' '+'\x1b[0m')
        dates=list(results.keys())
        for d in dates[-28:]:
            print('\x1b[48;5;0m\x1b[38;5;15m['+time.strftime('%Y.%m.%d',time.strptime(d,'%Y%m%d'))+']',end="\x1b[48;5;0m\n ")
            results[d]=DictSubSortNat(**results[d])
            tot=0
            for b in results[d]:
                print('\x1b[48;5;0m\x1b[38;5;111m'+format_bin(b)+'='+'\x1b[0m',end='')
                for c in results[d][b]:
                    print('\x1b[48;5;0m\x1b[38;5;048m'+c+"(x"+__builtins__.str(results[d][b][c])+')'+'\x1b[0m',end='\x1b[48;5;0m ')
                    tot+=int(c)*int(results[d][b][c])
            print('\x1b[48;5;0m')
            print('\x1b[48;5;0m\x1b[38;5;226mTotal: '+__builtins__.str(tot)+'\x1b[0m')
            print('\x1b[48;5;0m')
    print('\x1b[48;5;0mPress any key to return')
    wait_key()
    clear_screen()

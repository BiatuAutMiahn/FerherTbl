#!/usr/bin/python3
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
from collections import OrderedDict
try:
    import readline
except ImportError:
    pass

class DictSubSortLen(OrderedDict):
    def __init__(self, **kwargs):
        super(DictSubSortLen, self).__init__()
        for key, value in sorted(kwargs.items(), reverse=False):
            if isinstance(value, dict):
                self[key] = DictSubSortLen(**value)
            else:
                self[key] = value

def clear_screen():
    command = "clear"
    if platform.system().lower()=="nt":
        command = "cls"
    subprocess.call(command)
    return subprocess.call(command) == 0

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

def sync_tables(update=True):
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
        if update:
            with open("tables.json") as f:
                new_tables=json.loads(f.read())
                new_tables.update(tables)
                tables=new_tables
        sort_tables()
        with open("tables.json","w+") as f:
            f.write(json.dumps(tables,indent=2))
    else:
        tables={}
    #time.sleep(0.2)
    os.remove("tables.lock")
    print("\rSyncing Tables...done     ")

def sync_usertables():
    print("\rSyncing User Tables...",end="")
    sys.stdout.flush()
    global usertables
    if os.path.isfile("usertables.lock"):
        print("\rSyncing User Tables, Waiting...",end="")
        sys.stdout.flush()
        while True:
            if not os.path.isfile("usertables.lock"):
                break
            time.sleep(0.1)
    open("usertables.lock",'a').close()
    if os.path.isfile("usertables.json"):
        with open("usertables.json") as f:
            usertables_new=json.loads(f.read())
            usertables_new.update(usertables)
            usertables=usertables_new
        with open("usertables.json","w+") as f:
            f.write(json.dumps(usertables,indent=2))
            f.flush()
    else:
        usertables={}
    time.sleep(0.2)
    os.remove("usertables.lock")
    print("\rSyncing User Tables...done     ")

def sync_users():
    print("\rSyncing Users...",end="")
    sys.stdout.flush()
    global users
    if os.path.isfile("users.lock"):
        print("\rSyncing Users, Waiting...",end="")
        sys.stdout.flush()
        while True:
            if not os.path.isfile("users.lock"):
                break
            time.sleep(0.1)
    open("users.lock",'a').close()
    if os.path.isfile("users.json"):
        with open("users.json") as f:
            users_new=json.loads(f.read())
            users_new.update(users)
            users=users_new
        with open("users.json","w+") as f:
            f.write(json.dumps(users,indent=2))
            f.flush()
    else:
        users={}
    time.sleep(0.2)
    os.remove("users.lock")
    print("\rSyncing Users...done     ")

def sort_tables():
    global tables
    tables=DictSubSortLen(**tables)

def sort_usertables():
    global usertables
    usertables=DictSubSortLen(**usertables)

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

clear_screen()
print("Initializing...")
users = {}
tables = {}
usertables = {}
sync_users()
sync_tables()
sync_usertables()
print(usertables)
colorama.init(autoreset=True)

user="test" # None
attempt=0
reset=False
date=None
table=None
stable=None
prod=None
today=time.strftime('%Y%m%d',time.localtime())
date=today
while True:
    clear_screen()
    print("[Table]")
    y=0
    for key in tables:
        if y==7:
            y=0
            if key==table:
                if len(key)==3:
                    print(' \x1b[0;30;47m'+key+'\x1b[0m'.rjust(4))
                elif len(key)==4:
                    print('\x1b[0;30;47m'+key+'\x1b[0m'.rjust(4))
            else:
                print(key.rjust(4))
        else:
            if key==table:
                if len(key)==3:
                    print(' \x1b[0;30;47m'+key+'\x1b[0m'.rjust(4),end=" ")
                elif len(key)==4:
                    print('\x1b[0;30;47m'+key+'\x1b[0m'.rjust(4),end=" ")
            else:
                print(key.rjust(4),end=" ")
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
                        if y==7:
                            y=0
                            if po==prod:
                                print('\x1b[0;30;47m'+po+'\x1b[0m'.rjust(4))
                            else:
                                print(po.rjust(4))
                        else:
                            if po==prod:
                                print('\x1b[0;30;47m'+po+'\x1b[0m'.rjust(4),end=" ")
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
                    if y==7:
                        y=0
                        if po==prod:
                            print('\x1b[0;30;47m'+po+'\x1b[0m'.rjust(4))
                        else:
                            print(po.rjust(4))
                    else:
                        if po==prod:
                            print('\x1b[0;30;47m'+po+'\x1b[0m'.rjust(4),end=" ")
                        else:
                            print(po.rjust(4),end=" ")
                        y+=1
                    if po==list(tables[table]['polist'].keys())[-1]:
                        print('')
                print('')
    if users[user]['role']=="user":
        if table is not None and prod is not None:
            total=0
            counts=[]
            if stable is not None:
                counts=usertables[user][date][table][stable]['polist'][prod]['counts']
            else:
                counts=usertables[user][date][table]['polist'][prod]['counts']
            if len(counts) > 0:
                print("[Counts]")
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
                print("  Total: "+str(total))
                print('')
    # if table is not None:
    #     if stable is not None:
    #         print(json.dumps(tables[table][stable],indent=2))
    #     else:
    #         print(json.dumps(tables[table],indent=2))
    inp=None
    while True:
        inp=input(":")
        if len(inp)>0:
            break
    if inp=='help':
        print("[Help]")
        print("Note: Anything in brackets [] are optional.")
        print(" /<Table>[,<SubTable>]    : Switch to Table/Subtable")
        print("     If a Table/SubTable does not exist, it will be created.")
        print(" /-<Table>[,<SubTable>]   : Remove a Table/SubTable")
        print(" <Product>                : Select/Add a Product Number")
        print(" -<Product>               : Remove a Product number")
        print(" +<Number>[*Multiplier]   : Add counts to the selected Product.")
        print(" --<Number>[*Multiplier]  : Subtract counts from the selected Product.")
        print('')
        print("[Examples]")
        print(" /090        : Switch to 090 Table")
        print(" /1100       : Switch to 1100 Table")
        print(" /1100.9906  : Switch to 9906 Subtable in 1100 Table")
        print(" /-383       : Remove 383 Table")
        print(" /-1100.9905 : Remove 9905 SubTable from 1100 Table")
        print(" +0611        : Select/Add Product 0611")
        print(" -0611       : Remove Product 0611 from Table")
        print(" ++1400       : Add Qty 1400 to Selected Product")
        print(" ++1400*4     : Add 4 Boxes of Qty 1400 to Selected Product")
        print(" --1400      : Subtract 1400 from Product")
        print(" --1400*2      : Subtract 2 boxes of 1400 from Product")
        print('')
        print("Press any key to continue...")
        wait_key()
        continue
    if users[user]['role']=="admin":
        if inp[0]=='/':
            if '.' in inp:
                spl=inp[1:].split('.')
                if inp[1]=='-':
                    spl=inp[2:].split('.')
                    if validate_input(spl[0]) or validate_input(spl[1]):
                        continue
                    time.sleep(1)
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
                        sync_tables(False)
                else:
                    if validate_input(spl[0]) or validate_input(spl[1]):
                        continue
                    if not spl[0] in tables:
                        tables[spl[0]]={}
                        tables[spl[0]]['type']='table'
                        tables[spl[0]]['times']={'created':time.strftime('%Y%m%d%H%M%S',time.localtime()),'modified':time.strftime('%Y%m%d%H%M%S',time.localtime()),'accessed':time.strftime('%Y%m%d%H%M%S',time.localtime())}
                    if not spl[1] in tables[spl[0]]:
                        tables[spl[0]]['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                        tables[spl[0]][spl[1]]={}
                        tables[spl[0]][spl[1]]['type']='subtable'
                        tables[spl[0]][spl[1]]['times']={'created':time.strftime('%Y%m%d%H%M%S',time.localtime()),'modified':time.strftime('%Y%m%d%H%M%S',time.localtime()),'accessed':time.strftime('%Y%m%d%H%M%S',time.localtime())}
                        tables[spl[0]][spl[1]]['polist']={}
                    table=spl[0]
                    stable=spl[1]
                    prod=None
                    tables[table]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    tables[table][stable]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    sync_tables()
            else:
                if inp[1]=='-':
                    if validate_input(inp[2:]):
                        continue
                    if inp[2:] not in tables:
                        print("Table not found")
                        time.sleep(2)
                        continue
                    tables.pop(inp[2:],None)
                    sync_tables(False)
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
                    else:
                        stable=None
                    table=inp[1:]
                    prod=None
                    tables[table]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    sync_tables()
        elif inp[0]=='-':
            if validate_input(inp[1:]):
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
                if inp[1:] in tables[table][stable]['polist']:
                    tables[table]['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    tables[table][stable]['polist'].pop(inp[1:],None)
                    tables[table][stable]['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    if prod==inp:
                        prod=None
                    sync_tables(False)
                else:
                    print("Product not in SubTable")
                    time.sleep(2)
                    continue
            else:
                if inp[1:] in tables[table]['polist']:
                    tables[table]['polist'].pop(inp[1:],None)
                    tables[table]['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    sync_tables()
                    if prod==inp:
                        prod=None
                else:
                    print("Product not in Table")
                    time.sleep(2)
                    continue
        elif inp[0:2]=='++':
            print("Admins cannot modify product counts")
            time.sleep(2)
            continue
        elif inp[0:2]=="--":
            print("Admins cannot modify product counts")
            time.sleep(2)
            continue
        elif inp[0]=="+":
            if table is not None:
                if validate_input(inp[1:]):
                    continue
                if not 'polist' in tables[table]:
                    if stable is None:
                        print("Please select a SubTable")
                        time.sleep(2)
                        continue
                    if inp[1:] not in tables[table][stable]['polist']:
                        print(inp)
                        time.sleep(2)
                        tables[table]['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                        tables[table][stable]['polist'][inp[1:]]={}
                        tables[table][stable]['polist'][inp[1:]]['times']={'created':time.strftime('%Y%m%d%H%M%S',time.localtime()),'modified':time.strftime('%Y%m%d%H%M%S',time.localtime()),'accessed':time.strftime('%Y%m%d%H%M%S',time.localtime())}
                        tables[table][stable]['polist'][inp[1:]]['counts']=[]
                        sort_tables()
                    tables[table]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    tables[table][stable]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    tables[table][stable]['polist'][inp[1:]]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    #tables[table]['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    prod=inp[1:]
                    sync_tables()
                else:
                    if inp[1:] not in list(tables[table]['polist'].keys()):
                        tables[table]['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                        tables[table]['polist'][inp[1:]]={}
                        tables[table]['polist'][inp[1:]]['times']={'created':time.strftime('%Y%m%d%H%M%S',time.localtime()),'modified':time.strftime('%Y%m%d%H%M%S',time.localtime()),'accessed':time.strftime('%Y%m%d%H%M%S',time.localtime())}
                        tables[table]['polist'][inp[1:]]['counts']=[]
                        sort_tables()
                        continue
                    tables[table]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    tables[table]['polist'][inp[1:]]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    prod=inp[1:]
                    sync_tables()
            else:
                print("Please select a Table")
                time.sleep(2)
                continue
        else:
            print("Invalid Input")
            time.sleep(2)
            continue
    elif users[user]['role']=="user":
        if not date in usertables[user]:
            usertables[user][date]={}
            # usertables[user][date]['times']={'created':time.strftime('%Y%m%d%H%M%S',time.localtime()),'modified':time.strftime('%Y%m%d%H%M%S',time.localtime()),'accessed':time.strftime('%Y%m%d%H%M%S',time.localtime())}
        if inp[0]=='/':
            if '.' in inp:
                spl=inp[1:].split('.')
                if inp[1]=='-':
                    spl=inp[2:].split('.')
                    if validate_input(spl[0]) or validate_input(spl[1]):
                        continue
                    time.sleep(1)
                    if spl[0] not in usertables[user][date]:
                        print("Table not found")
                        time.sleep(2)
                        continue
                    if spl[1] not in usertables[user][date][spl[0]]:
                        print("SubTable not found")
                        time.sleep(2)
                        continue
                    else:
                        usertables[user][date][spl[0]].pop(spl[1],None)
                        # usertables[user][date][spl[0]][spl[1]]['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                        if stable==spl[1]:
                            stable=None
                            prod=None
                        sync_usertables(False)
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
                    if not spl[0] in usertables[user][date]:
                        usertables[user][date][spl[0]]={}
                        usertables[user][date][spl[0]]['type']='table'
                        # usertables[user][date][spl[0]]['times']={'created':time.strftime('%Y%m%d%H%M%S',time.localtime()),'modified':time.strftime('%Y%m%d%H%M%S',time.localtime()),'accessed':time.strftime('%Y%m%d%H%M%S',time.localtime())}
                        sort_usertables()
                    if not spl[1] in usertables[user][date][spl[0]]:
                        # usertables[user][date][spl[0]]['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                        usertables[user][date][spl[0]][spl[1]]={}
                        usertables[user][date][spl[0]][spl[1]]['type']='subtable'
                        # usertables[user][date][spl[0]][spl[1]]['times']={'created':time.strftime('%Y%m%d%H%M%S',time.localtime()),'modified':time.strftime('%Y%m%d%H%M%S',time.localtime()),'accessed':time.strftime('%Y%m%d%H%M%S',time.localtime())}
                        usertables[user][date][spl[0]][spl[1]]['polist']={}
                        sort_usertables()
                    table=spl[0]
                    stable=spl[1]
                    prod=None
                    tables[table]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    tables[table][stable]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    # usertables[user][date][table]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    # usertables[user][date][table][stable]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    sync_tables()
                    sync_usertables()
            else:
                if inp[1]=='-':
                    if validate_input(inp[2:]):
                        continue
                    if inp[2:] not in usertables[user][date]:
                        print("Table not found")
                        time.sleep(2)
                        continue
                    usertables[user][date].pop(inp[2:],None)
                    # usertables[user][date][table]['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    sync_tables(False)
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
                    if not inp[1:] in usertables[user][date]:
                        usertables[user][date][inp[1:]]={}
                        usertables[user][date][inp[1:]]['type']='table'
                        # usertables[user][date][inp[1:]]['times']={'created':time.strftime('%Y%m%d%H%M%S',time.localtime()),'modified':time.strftime('%Y%m%d%H%M%S',time.localtime()),'accessed':time.strftime('%Y%m%d%H%M%S',time.localtime())}
                        usertables[user][date][inp[1:]]['polist']={}
                        sort_usertables()
                    else:
                        stable=None
                    table=inp[1:]
                    prod=None
                    tables[table]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    # usertables[user][date][table]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    sync_usertables()
                    sync_tables()
        elif inp[0:2]=='++':
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
            if '*' in inp[2:]:
                spl=inp[2:].split('*')
                if validate_input(spl[0],True) or validate_input(spl[1],True):
                    continue
                if stable is not None:
                    set=False
                    if len(usertables[user][date][table][stable]['polist'][prod]['counts']) > 0:
                        for i,c in enumerate(usertables[user][date][table][stable]['polist'][prod]['counts']):
                            if '*' in c:
                                splc=c.split('*')
                                if splc[0]==spl[0]:
                                    usertables[user][date][table][stable]['polist'][prod]['counts'][i]=splc[0]+"*"+str(int(splc[1])+int(spl[1]))
                                    set=True
                                    break
                    if not set:
                        usertables[user][date][table][stable]['polist'][prod]['counts'].append(spl[0]+"*"+spl[1])
                else:
                    set=False
                    if len(usertables[user][date][table]['polist'][prod]['counts']) > 0:
                        for i,c in enumerate(usertables[user][date][table]['polist'][prod]['counts']):
                            if '*' in c:
                                splc=c.split('*')
                                if splc[0]==spl[0]:
                                    usertables[user][date][table]['polist'][prod]['counts'][i]=splc[0]+"*"+str(int(splc[1])+int(spl[1]))
                                    set=True
                                    break
                            elif c==spl[0]:
                                usertables[user][date][table]['polist'][prod]['counts'][i]=spl[0]+"*"+str(int(spl[1])+1)
                                set=True
                                break
                    if not set:
                        usertables[user][date][table]['polist'][prod]['counts'].append(spl[0]+"*"+spl[1])
            else:
                if validate_input(inp[2:],True):
                    continue
                if stable is not None:
                    set=False
                    if len(usertables[user][date][table][stable]['polist'][prod]['counts']) > 0:
                        for i,c in enumerate(usertables[user][date][table][stable]['polist'][prod]['counts']):
                            if '*' in c:
                                spl=c.split('*')
                                if spl[0]==inp[2:]:
                                    usertables[user][date][table][stable]['polist'][prod]['counts'][i]=spl[0]+"*"+str(int(spl[1])+1)
                                    set=True
                                    break
                            elif inp[2:]==c:
                                usertables[user][date][table][stable]['polist'][prod]['counts'][i]=inp[2:]+"*2"
                                set=True
                                break
                    if not set:
                        usertables[user][date][table][stable]['polist'][prod]['counts'].append(inp[2:])
                else:
                    set=False
                    if len(usertables[user][date][table]['polist'][prod]['counts']) > 0:
                        for i,c in enumerate(usertables[user][date][table]['polist'][prod]['counts']):
                            if '*' in c:
                                spl=c.split('*')
                                if spl[0]==inp[2:]:
                                    usertables[user][date][table]['polist'][prod]['counts'][i]=spl[0]+"*"+str(int(spl[1])+1)
                                    set=True
                                    break
                            elif inp[2:]==c:
                                usertables[user][date][table]['polist'][prod]['counts'][i]=inp[2:]+"*2"
                                set=True
                                break
                    if not set:
                        usertables[user][date][table]['polist'][prod]['counts'].append(inp[2:])
        elif inp[0:2]=="--":
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
            if '*' in inp[2:]:
                spl=inp[2:].split('*')
                if validate_input(spl[0],True) or validate_input(spl[1],True):
                    continue
                if stable is not None:
                    set=False
                    rm=None
                    if len(usertables[user][date][table][stable]['polist'][prod]['counts']) > 0:
                        for i,c in enumerate(usertables[user][date][table][stable]['polist'][prod]['counts']):
                            if '*' in c:
                                splc=c.split('*')
                                if splc[0]==spl[0]:
                                    if int(splc[1])-int(spl[1])==1:
                                        usertables[user][date][table][stable]['polist'][prod]['counts'][i]=splc[0]
                                    if int(splc[1])-int(spl[1])<=0:
                                        rm=c
                                    else:
                                        usertables[user][date][table][stable]['polist'][prod]['counts'][i]=splc[0]+"*"+str(int(splc[1])-int(spl[1]))
                                    set=True
                                    break
                    if not set:
                        usertables[user][date][table][stable]['polist'][prod]['counts'].remove(spl[0]+"*"+spl[1])
                    if rm is not None:
                        usertables[user][date][table][stable]['polist'][prod]['counts'].remove(rm)
                else:
                    set=False
                    rm=None
                    if len(usertables[user][date][table][stable]['polist'][prod]['counts']) > 0:
                        for i,c in enumerate(usertables[user][date][table][stable]['polist'][prod]['counts']):
                            if '*' in c:
                                splc=c.split('*')
                                if splc[0]==spl[0]:
                                    if int(splc[1])-int(spl[1])==1:
                                        usertables[user][date][table]['polist'][prod]['counts'][i]=splc[0]
                                    if int(splc[1])-int(spl[1])<=0:
                                        rm=c
                                    else:
                                        usertables[user][date][table]['polist'][prod]['counts'][i]=splc[0]+"*"+str(int(splc[1])-int(spl[1]))
                                    set=True
                                    break
                    if not set:
                        usertables[user][date][table]['polist'][prod]['counts'].remove(spl[0]+"*"+spl[1])
                    if rm is not None:
                        usertables[user][date][table]['polist'][prod]['counts'].remove(rm)
            else:
                if validate_input(inp[2:],True):
                    continue
                if stable is not None:
                    set=False
                    rm=None
                    if len(usertables[user][date][table][stable]['polist'][prod]['counts']) > 0:
                        for i,c in enumerate(usertables[user][date][table][stable]['polist'][prod]['counts']):
                            if '*' in c:
                                spl=c.split('*')
                                if spl[0]==inp[2:]:
                                    if int(spl[1])-1==1:
                                        usertables[user][date][table][stable]['polist'][prod]['counts'][i]=spl[0]
                                    elif int(spl[1])-1<=0:
                                        rm=c
                                    else:
                                        usertables[user][date][table][stable]['polist'][prod]['counts'][i]=spl[0]+"*"+str(int(spl[1])-1)
                                    set=True
                                    break
                    if not set:
                        usertables[user][date][table][stable]['polist'][prod]['counts'].remove(inp[2:])
                    if rm is not None:
                        usertables[user][date][table][stable]['polist'][prod]['counts'].remove(rm)
                else:
                    set=False
                    rm=None
                    if len(usertables[user][date][table]['polist'][prod]['counts']) > 0:
                        for i,c in enumerate(usertables[user][date][table]['polist'][prod]['counts']):
                            if '*' in c:
                                spl=c.split('*')
                                if spl[0]==inp[2:]:
                                    if int(spl[1])-1==1:
                                        usertables[user][date][table]['polist'][prod]['counts'][i]=spl[0]
                                    elif int(spl[1])-1<=0:
                                        rm=c
                                    else:
                                        usertables[user][date][table]['polist'][prod]['counts'][i]=spl[0]+"*"+str(int(spl[1])-1)
                                    set=True
                                    break
                    if not set:
                        usertables[user][date][table]['polist'][prod]['counts'].remove(inp[2:])
                    if rm is not None:
                        usertables[user][date][table]['polist'][prod]['counts'].remove(rm)
        elif inp[0]=='-':
            if validate_input(inp[1:]):
                continue
            if table is None:
                print("Please select a Table")
                time.sleep(2)
                continue
            if not 'polist' in usertables[user][date][table]:
                if stable is None:
                    print("Please select a SubTable")
                    time.sleep(2)
                    continue
                if inp[1:] in usertables[user][date][table][stable]['polist']:
                    # usertables[user][date][table]['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    usertables[user][date][table][stable]['polist'].pop(inp[1:],None)
                    # usertables[user][date][table][stable]['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    sync_usertables(False)
                    if prod==inp:
                        prod=None
                else:
                    print("Product not in SubTable")
                    time.sleep(2)
                    continue
            else:
                if inp[1:] in usertables[user][date][table]['polist']:
                    usertables[user][date][table]['polist'].pop(inp[1:],None)
                    # usertables[user][date][table]['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    sync_usertables()
                    if prod==inp:
                        prod=None
                else:
                    print("Product not in Table")
                    time.sleep(2)
                    continue
            if prod is None:
                print("Please select a Product")
                time.sleep(2)
                continue
            if '*' in inp[2:]:
                spl=inp[2:].split('*')
                if validate_input(spl[0],True) or validate_input(spl[1],True):
                    continue
                print(spl)
            else:
                if validate_input(inp[2:],True):
                    continue
                print(inp[2:])
        elif inp[0]=="+":
            if table is not None:
                if validate_input(inp[1:]):
                    continue
                if not 'polist' in usertables[user][date][table] or not 'polist' in tables[table]:
                    if stable is None:
                        print("Please select a SubTable")
                        time.sleep(2)
                        continue
                    if inp[1:] not in tables[table][stable]['polist']:
                        print(inp)
                        time.sleep(2)
                        tables[table]['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                        tables[table][stable]['polist'][inp[1:]]={}
                        tables[table][stable]['polist'][inp[1:]]['times']={'created':time.strftime('%Y%m%d%H%M%S',time.localtime()),'modified':time.strftime('%Y%m%d%H%M%S',time.localtime()),'accessed':time.strftime('%Y%m%d%H%M%S',time.localtime())}
                        tables[table][stable]['polist'][inp[1:]]['counts']=[]
                        sort_tables()
                    tables[table]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    tables[table][stable]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    tables[table][stable]['polist'][inp[1:]]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    if inp[1:] not in usertables[user][date][table][stable]['polist']:
                        print(inp)
                        time.sleep(2)
                        # usertables[user][date][table]['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                        usertables[user][date][table][stable]['polist'][inp[1:]]={}
                        # usertables[user][date][table][stable]['polist'][inp[1:]]['times']={'created':time.strftime('%Y%m%d%H%M%S',time.localtime()),'modified':time.strftime('%Y%m%d%H%M%S',time.localtime()),'accessed':time.strftime('%Y%m%d%H%M%S',time.localtime())}
                        usertables[user][date][table][stable]['polist'][inp[1:]]['counts']=[]
                        sort_usertables()
                    # usertables[user][date][table]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    # usertables[user][date][table][stable]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    # usertables[user][date][table][stable]['polist'][inp[1:]]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    prod=inp[1:]
                    sync_usertables()
                    sync_tables()
                else:
                    if inp[1:] not in tables[table]['polist']:
                        tables[table]['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                        tables[table]['polist'][inp[1:]]={}
                        tables[table]['polist'][inp[1:]]['times']={'created':time.strftime('%Y%m%d%H%M%S',time.localtime()),'modified':time.strftime('%Y%m%d%H%M%S',time.localtime()),'accessed':time.strftime('%Y%m%d%H%M%S',time.localtime())}
                        tables[table]['polist'][inp[1:]]['counts']=[]
                        sort_tables()
                    if inp[1:] not in usertables[user][date][table]['polist']:
                        # usertables[user][date][table]['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                        usertables[user][date][table]['polist'][inp[1:]]={}
                        # usertables[user][date][table]['polist'][inp[1:]]['times']={'created':time.strftime('%Y%m%d%H%M%S',time.localtime()),'modified':time.strftime('%Y%m%d%H%M%S',time.localtime()),'accessed':time.strftime('%Y%m%d%H%M%S',time.localtime())}
                        usertables[user][date][table]['polist'][inp[1:]]['counts']=[]
                        sort_usertables()
                    tables[table]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    tables[table]['polist'][inp[1:]]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    # usertables[user][date][table]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    # usertables[user][date][table]['polist'][inp[1:]]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                    prod=inp[1:]
                    sync_usertables()
                    sync_tables()
            else:
                print("Please select a Table")
                time.sleep(2)
                continue
        else:
            print("Invalid Input")
            time.sleep(2)
            continue

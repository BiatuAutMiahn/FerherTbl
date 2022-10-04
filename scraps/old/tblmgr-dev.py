#!/usr/bin/python3
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
        if verify_password(users[username]["key"],password):
            print("Login successful")
            return True
    return False

def login():
    global user
    while True:
        username = input("User: ")
        if len(username) > 0:
            break
    while True:
        password = stdiomask.getpass()
        if len(password) > 0:
            break
    if loginauth(username, password):
        user=username
        return True
    else:
        return False

def fail_login():
    exit()

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


def sync_totals():
    print("\rSyncing Product Totals...",end="")
    sys.stdout.flush()
    global totals
    if os.path.isfile("totals.lock"):
        print("\rSyncing Product Totals, Waiting...",end="")
        sys.stdout.flush()
        while True:
            if not os.path.isfile("totals.lock"):
                break
            time.sleep(0.1)
    open("totals.lock",'a').close()
    if os.path.isfile("totals.json"):
        with open("totals.json") as f:
            totals_new=json.loads(f.read())
            totals_new.update(totals)
            totals=totals_new
        with open("totals.json","w+") as f:
            f.write(json.dumps(totals,indent=2))
            f.flush()
    else:
        totals={}
    time.sleep(0.2)
    os.remove("totals.lock")
    print("\rSyncing Product Totals...done     ")

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
    # print(user)
    # print(usertables)
    # time.sleep(5)
    # usertables=DictSubSortLen(**usertables)


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
totals = {}
sync_users()
sync_tables()
sync_usertables()
sync_totals()
colorama.init(autoreset=True)
print('Starting Login...')
time.sleep(2)
clear_screen()
attempt=0
reset=False
today=time.strftime('%Y%m%d',time.localtime())
date=today
user=None
while True:
    while True:
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
    if 'reset_key' in users[user]:
        if users[user]['reset_key']:
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
                                users[user]['key']=newkey
                                users[user]['reset_key']=False
                                write_users()
                                break
                            else:
                                retry=True
                                print("Password mismatch!")
                                break
                    if not retry:
                        break
    if reset:
        user=None
        attempt=0
        clear_screen()
        continue
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
            if user=="admin":
                print('--Admin Actions---------------------------------------------')
                print('genasign : Assigns each user a set of Product Tables at random. (Based on product count, Not yet Implemented)')
                print('gentmpl  : Generates PDFs for updated Product Tables. (Not yet Implemented)')
                print('emltmpl  : Emails Product Tables for distribution. (Not yet Implemented)')
                print("rmusr    : Remove a User.")
                print("lsusr    : List Users.")
                print("addusr   : Add a new User.")
        elif cmd=="logout":
            user=None
            attempt=0
            clear_screen()
            break
        elif cmd=="exptotals":
            with open('csv/'+date+'.csv', mode='w') as csv_file:
                fieldnames = ['po', 'total']
                writer = csv.writer(csv_file,delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL,lineterminator='\n')
                writer.writerow(fieldnames)
                for p in totals[date]:
                    # print(p+',',totals[date][p])
                    writer.writerow([p,totals[date][p]])

        elif cmd=="mytables":
            table=None
            stable=None
            prod=None
            if users[user]['role']=='user':
                if not date in usertables[user]:
                    usertables[user][date]={}
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
                inp=None
                while True:
                    inp=input(":")
                    if len(inp)>0:
                        break
                if inp=='return':
                    break
                if inp=='submit':
                    if users[user]['role']=='admin':
                        print("Admins cannot submit counts")
                        time.sleep(2)
                        continue
                    elif users[user]['role']=='user':
                        if not date in totals:
                            totals[date]={}
                        for t in usertables[user][date]:
                            if 'polist' in usertables[user][date][t]:
                                if len(usertables[user][date][t]['polist'])>0:
                                    for p in usertables[user][date][t]['polist']:
                                        if len(usertables[user][date][t]['polist'][p]['counts'])>0:
                                            if not t+p in totals[date]:
                                                totals[date][t+p]=0# {'boxes':0,'partials':0,'total':0}
                                            total=0
                                            for c in usertables[user][date][t]['polist'][p]['counts']:
                                                if '*' in c:
                                                    spl=c.split('*')
                                                    total+=int(spl[0])*int(spl[1])
                                                else:
                                                    total+=int(c)
                                            totals[date][t+p]=total
                                            # print(t+p+','+str(totals))
                            else:
                                for s in usertables[user][date][t]:
                                    if s in ['type']:
                                        continue
                                    for p in usertables[user][date][t][s]['polist']:
                                        if len(usertables[user][date][t][s]['polist'][p]['counts'])>0:
                                            if not t+p+s in totals[date]:
                                                totals[date][t+p+s]=0 # {'boxes':0,'partials':0,'total':0}
                                            total=0
                                            for c in usertables[user][date][t][s]['polist'][p]['counts']:
                                                if '*' in c:
                                                    spl=c.split('*')
                                                    total+=int(spl[0])*int(spl[1])
                                                else:
                                                    total+=int(c)
                                            totals[date][t+p+s]=total
                        sync_totals()
                        continue
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
                    print(" ++0611        : Select/Add Product 0611")
                    print(" --0611       : Remove Product 0611 from Table")
                    print(" +1400       : Add Qty 1400 to Selected Product")
                    print(" +1400*4     : Add 4 Boxes of Qty 1400 to Selected Product")
                    print(" -1400      : Subtract 1400 from Product")
                    print(" -1400*2      : Subtract 2 boxes of 1400 from Product")
                    print('')
                    print("Press any key to continue...")
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
                            if users[user]['role']=='admin':
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
                            elif users[user]['role']=='user':
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
                                sync_usertables(False)
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
                            if users[user]['role']=='user':
                                if not spl[0] in usertables[user][date]:
                                    usertables[user][date][spl[0]]={}
                                    usertables[user][date][spl[0]]['type']='table'
                                if not spl[1] in usertables[user][date][spl[0]]:
                                    usertables[user][date][spl[0]][spl[1]]={}
                                    usertables[user][date][spl[0]][spl[1]]['type']='subtable'
                                    usertables[user][date][spl[0]][spl[1]]['polist']={}
                                sort_usertables()
                            table=spl[0]
                            stable=spl[1]
                            prod=None
                            tables[table]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                            tables[table][stable]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                            sync_tables()
                            if users[user]['role']=='user':
                                sync_usertables()
                    else:
                        if inp[1]=='-':
                            if validate_input(inp[2:]):
                                continue
                            if users[user]['role']=='admin':
                                if inp[2:] not in tables:
                                    print("Table not found")
                                    time.sleep(2)
                                    continue
                                tables.pop(inp[2:],None)
                                sync_tables(False)
                            elif users[user]['role']=='user':
                                if inp[2:] not in usertables[user][date]:
                                    print("Table not found")
                                    time.sleep(2)
                                    continue
                                usertables[user][date].pop(inp[2:],None)
                                sync_usertables(False)
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
                                if users[user]['role']=='admin':
                                    stable=None
                            if users[user]['role']=='user':
                                if not inp[1:] in usertables[user][date]:
                                    usertables[user][date][inp[1:]]={}
                                    usertables[user][date][inp[1:]]['type']='table'
                                    usertables[user][date][inp[1:]]['polist']={}
                                    sort_usertables()
                                else:
                                    stable=None
                            table=inp[1:]
                            prod=None
                            tables[table]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                            sync_tables()
                            if users[user]['role']=='user':
                                sync_usertables()
                elif inp[0:2]=="--":
                    if validate_input(inp[2:]):
                        continue
                    if table is None:
                        print("Please select a Table")
                        time.sleep(2)
                        continue
                    if users[user]['role']=='admin':
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
                                sync_tables(False)
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
                    elif users[user]['role']=='user':
                        if not 'polist' in usertables[user][date][table]:
                            if stable is None:
                                print("Please select a SubTable")
                                time.sleep(2)
                                continue
                            if inp[2:] in usertables[user][date][table][stable]['polist']:
                                usertables[user][date][table][stable]['polist'].pop(inp[2:],None)
                                sync_usertables(False)
                                if prod==inp:
                                    prod=None
                            else:
                                print("Product not in SubTable")
                                time.sleep(2)
                            continue
                        else:
                            if inp[2:] in usertables[user][date][table]['polist']:
                                usertables[user][date][table]['polist'].pop(inp[2:],None)
                                sync_usertables()
                                if prod==inp:
                                    prod=None
                            else:
                                print("Product not in Table")
                                time.sleep(2)
                                continue
                elif inp[0:2]=='++':
                    if table is not None:
                        if validate_input(inp[2:]):
                            continue
                        if users[user]['role']=='admin':
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
                                    tables[table][stable]['polist'][inp[2:]]['counts']=[]
                                    sort_tables()
                                tables[table]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                                tables[table][stable]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                                tables[table][stable]['polist'][inp[1:]]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                                #tables[table]['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                                prod=inp[2:]
                                sync_tables()
                            else:
                                if inp[2:] not in tables[table]['polist']:
                                    tables[table]['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                                    tables[table]['polist'][inp[2:]]={}
                                    tables[table]['polist'][inp[2:]]['times']={'created':time.strftime('%Y%m%d%H%M%S',time.localtime()),'modified':time.strftime('%Y%m%d%H%M%S',time.localtime()),'accessed':time.strftime('%Y%m%d%H%M%S',time.localtime())}
                                    tables[table]['polist'][inp[2:]]['counts']=[]
                                    sort_tables()
                                    continue
                        elif users[user]['role']=='user':
                            if not 'polist' in usertables[user][date][table] or not 'polist' in tables[table]:
                                if stable is None:
                                    print("Please select a SubTable")
                                    time.sleep(2)
                                    continue
                                if inp[2:] not in tables[table][stable]['polist']:
                                    time.sleep(2)
                                    tables[table]['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                                    tables[table][stable]['polist'][inp[2:]]={}
                                    tables[table][stable]['polist'][inp[2:]]['times']={'created':time.strftime('%Y%m%d%H%M%S',time.localtime()),'modified':time.strftime('%Y%m%d%H%M%S',time.localtime()),'accessed':time.strftime('%Y%m%d%H%M%S',time.localtime())}
                                    tables[table][stable]['polist'][inp[2:]]['counts']=[]
                                    sort_tables()
                                if inp[2:] not in usertables[user][date][table][stable]['polist']:
                                    time.sleep(2)
                                    usertables[user][date][table][stable]['polist'][inp[2:]]={}
                                    usertables[user][date][table][stable]['polist'][inp[2:]]['counts']=[]
                                    sort_usertables()
                                tables[table]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                                tables[table][stable]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                                tables[table][stable]['polist'][inp[2:]]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                            else:
                                if inp[2:] not in tables[table]['polist']:
                                    tables[table]['times']['modified']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                                    tables[table]['polist'][inp[2:]]={}
                                    tables[table]['polist'][inp[2:]]['times']={'created':time.strftime('%Y%m%d%H%M%S',time.localtime()),'modified':time.strftime('%Y%m%d%H%M%S',time.localtime()),'accessed':time.strftime('%Y%m%d%H%M%S',time.localtime())}
                                    tables[table]['polist'][inp[2:]]['counts']=[]
                                    sort_tables()
                                if inp[2:] not in usertables[user][date][table]['polist']:
                                    usertables[user][date][table]['polist'][inp[2:]]={}
                                    usertables[user][date][table]['polist'][inp[2:]]['counts']=[]
                                    tables[table]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                                    tables[table]['polist'][inp[2:]]['times']['accessed']=time.strftime('%Y%m%d%H%M%S',time.localtime())
                                    sort_usertables()
                            prod=inp[2:]
                            sync_tables()
                            if users[user]['role']=='user':
                                sync_usertables()
                    else:
                        print("Please select a Table")
                        time.sleep(2)
                        continue
                elif inp[0]=="+":
                    if users[user]['role']=="admin":
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
                    if '*' in inp[1:]:
                        spl=inp[1:].split('*')
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
                            sync_usertables()
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
                            sync_usertables()
                    else:
                        if validate_input(inp[1:],True):
                            continue
                        if stable is not None:
                            set=False
                            if len(usertables[user][date][table][stable]['polist'][prod]['counts']) > 0:
                                for i,c in enumerate(usertables[user][date][table][stable]['polist'][prod]['counts']):
                                    if '*' in c:
                                        spl=c.split('*')
                                        if spl[0]==inp[1:]:
                                            usertables[user][date][table][stable]['polist'][prod]['counts'][i]=spl[0]+"*"+str(int(spl[1])+1)
                                            set=True
                                            break
                                    elif inp[1:]==c:
                                        usertables[user][date][table][stable]['polist'][prod]['counts'][i]=inp[1:]+"*2"
                                        set=True
                                        break
                            if not set:
                                usertables[user][date][table][stable]['polist'][prod]['counts'].append(inp[1:])
                            sync_usertables()
                        else:
                            set=False
                            if len(usertables[user][date][table]['polist'][prod]['counts']) > 0:
                                for i,c in enumerate(usertables[user][date][table]['polist'][prod]['counts']):
                                    if '*' in c:
                                        spl=c.split('*')
                                        if spl[0]==inp[1:]:
                                            usertables[user][date][table]['polist'][prod]['counts'][i]=spl[0]+"*"+str(int(spl[1])+1)
                                            set=True
                                            break
                                    elif inp[1:]==c:
                                        usertables[user][date][table]['polist'][prod]['counts'][i]=inp[1:]+"*2"
                                        set=True
                                        break
                            if not set:
                                usertables[user][date][table]['polist'][prod]['counts'].append(inp[1:])
                            sync_usertables()
                elif inp[0]=='-':
                    if users[user]['role']=="admin":
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
                    if '*' in inp[1:]:
                        spl=inp[1:].split('*')
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
                            sync_usertables()
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
                            sync_usertables()
                    else:
                        if validate_input(inp[1:],True):
                            continue
                        if stable is not None:
                            set=False
                            rm=None
                            if len(usertables[user][date][table][stable]['polist'][prod]['counts']) > 0:
                                for i,c in enumerate(usertables[user][date][table][stable]['polist'][prod]['counts']):
                                    if '*' in c:
                                        spl=c.split('*')
                                        if spl[0]==inp[1:]:
                                            if int(spl[1])-1==1:
                                                usertables[user][date][table][stable]['polist'][prod]['counts'][i]=spl[0]
                                            elif int(spl[1])-1<=0:
                                                rm=c
                                            else:
                                                usertables[user][date][table][stable]['polist'][prod]['counts'][i]=spl[0]+"*"+str(int(spl[1])-1)
                                            set=True
                                            break
                            if not set:
                                usertables[user][date][table][stable]['polist'][prod]['counts'].remove(inp[1:])
                            if rm is not None:
                                usertables[user][date][table][stable]['polist'][prod]['counts'].remove(rm)
                            sync_usertables()
                        else:
                            set=False
                            rm=None
                            if len(usertables[user][date][table]['polist'][prod]['counts']) > 0:
                                for i,c in enumerate(usertables[user][date][table]['polist'][prod]['counts']):
                                    if '*' in c:
                                        spl=c.split('*')
                                        if spl[0]==inp[1:]:
                                            if int(spl[1])-1==1:
                                                usertables[user][date][table]['polist'][prod]['counts'][i]=spl[0]
                                            elif int(spl[1])-1<=0:
                                                rm=c
                                            else:
                                                usertables[user][date][table]['polist'][prod]['counts'][i]=spl[0]+"*"+str(int(spl[1])-1)
                                            set=True
                                            break
                            if not set:
                                usertables[user][date][table]['polist'][prod]['counts'].remove(inp[1:])
                            if rm is not None:
                                usertables[user][date][table]['polist'][prod]['counts'].remove(rm)
                            sync_usertables()
                else:
                    print("Invalid Input")
                    time.sleep(2)
                    continue
            # submit    : Submit's totals to team lead/supervisor
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
            if not users[user]['role']=="admin":
                print("Unauthorized command!")
                time.sleep(2)
                continue
            read_users()
            print('')
            print("[ListUsers]")
            for u in users.keys():
                print(u)
        elif cmd=="modusr":
            read_users()
            print('')
            if not users[user]['role']=="admin":
                print("[ListUsers]")
                for u in users.keys():
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
                                        users[newusr]=users.pop(usr)
                                        write_users()
                                        break
                                else:
                                    print("Invalid User.")
                            break
                    else:
                        print("Invalid User.")
            elif not users[user]['role']=="user":
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
                                        users[newusr]=users.pop(user)
                                        write_users()
                                        break
                                    elif consent=="no":
                                        break
                            break
                    else:
                        print("Invalid User.")
        elif cmd=="rmusr":
            if not users[user]['role']=="admin":
                print("Unauthorized command!")
                time.sleep(2)
                continue
            sync_users()
            print('')
            print("[ListUsers]")
            for u in users.keys():
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
                        users.pop(usr)
                        sync_users()
                        break
                else:
                    print("Invalid User.")
        elif cmd=="rstpw":
            sync_users()
            print('')
            if users[user]['role']=="admin":
                print("[ListUsers]")
                for u in users.keys():
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
                            users[usr]['key']=key
                            users[usr]['reset_key']=True
                            print("Temporary password is "+tempkey+'.')
                            sync_users()
                            break
                    else:
                        print("Invalid User.")
            elif users[user]['role']=='user':
                print("[ResetPassword]")
                while True:
                    consent=input("Are you Sure? [yes/no]: ")
                    if len(consent)>0:
                        if consent=="yes":
                            tempkey=str(random.randint(1000,9999))
                            key=hash_password(tempkey)
                            users[user]['key']=key
                            users[user]['reset_key']=True
                            print("Temporary password is "+tempkey+'.')
                            sync_users()
                            break
                        elif consent=="no":
                            break
        elif cmd=="addusr":
            if not users[user]['role']=="admin":
                print("Unauthorized command!")
                time.sleep(2)
                continue
            sync_users()
            print('')
            print("[ListUsers]")
            for u in users.keys():
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
                        users[newusr]={'key': key,'reset_key': True}
                        print("Temporary pin is "+tempkey+'.')
                        sync_users()
                        break
                else:
                    print("Invalid User.")
        elif cmd=="exit":
            exit()
        else:
            print("Invalid command.")
        print('')

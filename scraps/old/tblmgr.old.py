#!/usr/bin/python3
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

def clear_screen():
    command = "clear"
    if platform.system().lower()=="nt":
        command = "cls"
    subprocess.call(command)
    return subprocess.call(command) == 0

def read_users():
    global users
    if os.path.isfile('users.old.json'):
        with open('users.old.json') as f:
            users=json.loads(f.read())

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

def write_users():
    with open('users.old.json','w+') as f:
        f.write(json.dumps(users,indent=4))


clear_screen()
users = None
read_users()

user=None
attempt=0
reset=False
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
    clear_screen()
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
        elif cmd=="mytables":
            print("Not yet implemented.")
            # /1100,9906 : Switch to/add table. eg; /<table>[,<subtable>]
            # /090
            # /383

            # /-1100,9906 : Deletes <table>/<subtable> from your profile
            # /-909

            # 0661       : Entering a number by itself will focus on a particular product number
            # --0661      : Deletes product number from table

            # -1600*2
            # -1600
            # -20
            # if removed count is exact, it will be removed

            # +1600*32   : Add counts, +<quantity>[*<multiplier>]
            # +500*6
            # +35
            # if added count is a duplicate, it will be summed.

            # !submit    : Submit's totals to team lead/supervisor
            # !review    : Switch to table from another date
            # !today     : Switch to today's table
            # !return    : Return to main screen

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
            read_users()
            if user=="admin":
                print('')
                print("[ListUsers]")
                for u in users.keys():
                    print(u)
            else:
                print("Unauthorized command!")
        elif cmd=="modusr":
            read_users()
            print('')
            if user=="admin":
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
            else:
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
            read_users()
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
                        write_users()
                        break
                else:
                    print("Invalid User.")
        elif cmd=="rstpw":
            read_users()
            print('')
            if user=="admin":
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
                            write_users()
                            break
                    else:
                        print("Invalid User.")
            else:
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
                            write_users()
                            break
                        elif consent=="no":
                            break
        elif cmd=="addusr":
            read_users()
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
                        write_users()
                        break
                else:
                    print("Invalid User.")
        elif cmd=="exit":
            exit()
        else:
            print("Invalid command.")
        print('')

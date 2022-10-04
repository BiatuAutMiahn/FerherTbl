import random
import string
import os
import sys
import time
import json



class FehTables():
    __table_db=jsonDB('tables')
    __notify=Notify()
    def __init__(self):
        __notify.RegisterListener(Alias=session.alias)
        __notify.RegisterReciever("Feh.InvalidateTables",self.Refresh())
    def Refresh(self):
        # Read TablesDB
        pass
    def Bump(self,Table,SubTable=None,Product=None,Revision=None):
        # Updates the last access time of Product
        pass
    def Remove(self,Table,SubTable=None,Product=None,Revision=None):
        # Removes Product from the Tables
        pass
    def Omit(self,Table,SubTable=None,Product=None,Revision=None):
        # Omit Product from the Tables
        pass
    def Add(self,Table,SubTable=None,Product=None,Revision=None):
        # Adds a new Product to Table
        pass
    def Modify(self,Table,SubTable=None,Product=None,Revision=None,Quantity=None,Description=None,DefaultBin=None):
        # Updates Metadata for Product
        pass
    def GetTables(self):
        #Get a List of Tables
        pass
    def GetProducts(self,Table,SubTable=None):
        # Get List of Products
        pass
    def GetRevisions(self,Table,SubTable=None,Product=None):
        # Get List of Revisions
        pass

class FehUser():
    pass

class User():
    pass
# class Notify:
#     __Recievers = []
#     __notify_db=jsonDB('notify')
#     def __init__(self,clientid):
#         self.ClientId = clientid
#     def Check(self):
#         self.__notify_db.WaitLock()
#         data=self.__notify_db.Read()
#
#     def Global(self,msg):
#         pass
#     def Node(self,alias,msg):
#         pass
#     def Client(self,clientid,msg):
#         pass
#     def User(self,user,msg):
#         pass
#     def RegisterReciever(self,callback):
#         pass

class Session:
    'Session Managment'
    __sessions_db=jsonDB('sessions')
    __notify=Notify()
    def __init__(self,alias,build):
        self.Alias = alias
        self.ClientId = ''
        self.Build = build
    def Start(self):
        tstamps=time.strftime('%Y%m%d%H%M%S',time.localtime())
        self.__sessions_db.Lock()
        data=self.__sessions_db.Read()
        print("Staring Session...",end="")
        sys.stdout.flush()
        self.ClientId = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(16))
        if not self.Alias in data:
            data[self.Alias]={}
        if not 'Clients' in data[self.Alias]:
            data[self.Alias]['Clients']={}
        if not self.ClientId in data[self.Alias]['Clients']:
            data[self.Alias]['Clients'][self.ClientId]={}
        if not 'build' in data[self.Alias]['Clients'][self.ClientId]:
            data[self.Alias]['Clients'][self.ClientId]['build']=self.Build
        if not 'user' in data[self.Alias]['Clients'][self.ClientId]:
            data[self.Alias]['Clients'][self.ClientId]['build']='Anon'
        if not 'times' in data[self.Alias]['Clients'][self.ClientId]:
            data[self.Alias]['Clients'][self.ClientId]['times']={'SessionStart':tstamps,'LastAck':tstamps}
            # notify[self.Alias][self.ClientId]['times']['last_ack']=time.strftime('%Y%m%d%H%M%S',time.localtime())
        print("\rStarting Session...done       ")
        self.__sessions_db.Write(data)
        self.__sessions_db.Unlock()
        __notify.RegisterListener(Alias=self.Alias,Client=self.ClientId)
        __notify.RegisterReciever("Session.UserIdentify",self.__UserIdentify())
        __notify.RegisterReciever("Session.KillSession",self.__KillSession())
        return True
    def __UserIdentify():
        pass
    def __KillSession():
        pass
    def Close(self):
        # tstamps=time.strftime('%Y%m%d%H%M%S',time.localtime())
        self.__sessions_db.Lock()
        data=self.__sessions_db.Read()
        print("Closing Session...",end="")
        sys.stdout.flush()
        if not self.Alias in data:
            data[self.Alias]={}
        if not 'Clients' in data[self.Alias]:
            data[self.Alias]['Clients']={}
        if self.ClientId in data[self.Alias]['Clients']:
            data[self.Alias]['Clients'].pop(self.ClientId,None)
        print("\rClosing Session...done       ")
        self.__sessions_db.Write(data)
        self.__sessions_db.Unlock()
        return True


class jsonDB:
    def __init__(self,dbname):
        self.__dbname=dbname
        if not os.path.isfile('data/'+self.__dbname+".json"):
            open('data/'+self.__dbname+".lock",'a').close()
            with open('data/'+self.__dbname+".json","w+") as f:
                f.write('{}')
                f.flush()
            os.remove('data/'+self.__dbname+".lock")
    def Read(self):
        ret={}
        if os.path.isfile('data/'+self.__dbname+".json"):
            print("Reading "+self.__dbname.capitalize()+"DB...",end="")
            sys.stdout.flush()
            try:
                with open('data/'+self.__dbname+".json",'r') as f:
                    ret=json.loads(f.read())
            except Exception as e:
                print("\rReading "+self.__dbname.capitalize()+"DB...Failed")
                raise e
            print("\rReading "+self.__dbname.capitalize()+"DB...Done")
        return ret
    def Write(self,data):
        if os.path.isfile('data/'+self.__dbname+".json"):
            print("Writing "+self.__dbname.capitalize()+"DB...",end="")
            sys.stdout.flush()
            try:
                with open('data/'+self.__dbname+".json","w+") as f:
                    f.write(json.dumps(data,indent=2))
                    f.flush()
            except Exception as e:
                print("\rWriting "+self.__dbname.capitalize()+"DB...Failed")
                raise e
            print("\rWriting "+self.__dbname.capitalize()+"DB...Done")
            return True
        return False
    def Lock(self):
        print("Aquiring "+self.__dbname.capitalize()+"DB Lock...",end="")
        sys.stdout.flush()
        if os.path.isfile('data/'+self.__dbname.capitalize()+".lock"):
            print("\rAquiring "+self.__dbname.capitalize()+"DB Lock, Waiting...",end="")
            sys.stdout.flush()
            semisil=True
            while True:
                if not os.path.isfile('data/'+self.__dbname+".lock"):
                    break
                time.sleep(0.1)
        open('data/'+self.__dbname+".lock",'a').close()
        print("\rAquiring "+self.__dbname.capitalize()+"DB Lock...done     ")
        return True
    def WaitLock(self):
        if os.path.isfile('data/'+self.__dbname.capitalize()+".lock"):
            print("Waiting  for "+self.__dbname.capitalize()+"DB Unlock...",end="")
            sys.stdout.flush()
            while True:
                if not os.path.isfile('data/'+self.__dbname+".lock"):
                    break
                time.sleep(0.1)
            print("\rWaiting for "+self.__dbname.capitalize()+"DB Unlock...done     ")
        return True
    def Unlock(self):
        print("Releasing "+self.__dbname.capitalize()+"DB Lock...",end="")
        sys.stdout.flush()
        if os.path.isfile('data/'+self.__dbname+".lock"):
            os.remove('data/'+self.__dbname+".lock")
        print("\rReleasing "+self.__dbname.capitalize()+"DB Lock...done     ")
        return True




def term(c):
    if session:
        session.Close()
    exit(c)

def SigCatch(signal, frame):
    term(0)

def LogException(*exc_info):
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
    print("An error has occurred, and has been reported.")
    print("Press any key to exit...")
    wait_key()
    term(1)

def HookExit():
    sys.excepthook = LogException
    signal.signal(signal.SIGINT, SigCatch)
    signal.signal(signal.SIGPIPE, SigCatch)
    signal.signal(signal.SIGHUP, SigCatch)


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

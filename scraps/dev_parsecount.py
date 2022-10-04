#!/usr/bin/python3
import re
import readline
import time

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

# while True:
    # inp=input(':')
    # if inp!='':
test=["+d252o,33,50*4,42,36*2,18,49,64,34","+50,34o*3,33o*2","+50,d243o,d253o"]
for t in test:
    print(t)
    inp=t
    if ',' in inp[1:]:
        if ",," in inp:
            inp=inp.replace(",,",",")
        spl=inp[1:].split(',')
        if validate_bin(spl[0]):
            for i in range(1,len(spl)):
                if '*' in spl[i]:
                    spla=spl[i].split('*')
                    if len(spla)>2:
                        print("  Too many multipliers")
                        time.sleep(2)
                        continue
                    print('  +'+spla[0]+','+spl[0]+'*'+spla[1])
                else:
                    print('  +'+spl[i]+','+spl[0])
        elif spl[0].isdigit():
            for i in range(1,len(spl)):
                if '*' in spl[i]:
                    spla=spl[i].split('*')
                    if len(spla)>2:
                        print("  Too many multipliers")
                        time.sleep(2)
                        continue
                    print('     +'+spl[0]+','+spla[0]+','+spla[1])
                    if validate_bin(spla[0]) and spla[1].isdigit():
                        print('  +'+spl[0]+','+spla[0]+'*'+spla[1])
                    elif validate_bin(spla[1]) and spla[0].isdigit():
                        print('  +'+spl[0]+','+spla[1]+'*'+spla[0])
                    else:
                        print("  Invalid Count")
                        time.sleep(2)
                        continue
                else:
                    if not validate_bin(spl[i]):
                        print("  Invalid Count")
                        time.sleep(2)
                        continue
                    print('  +'+spl[0]+','+spl[i])
        else:
            print("  Invalid Count")
            time.sleep(2)
    else:
        print('  '+inp)

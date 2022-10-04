
import curses
import os.path
import json
import binascii

ScreenH = 0
ScreenW = 0
CursorX = 1
CursorY = 1

chars = ['0','1','2','3','4','5','6','7','8','9','X','L','/','-',',','\r','\n']

def my_raw_input(stdscr, r, c):
    input=''
    #stdscr.getstr(r + 1, c, 16)
    curses.noecho()
    stdscr.move(ScreenH-2,0)
    #stdscr.addstr(r, c, prompt_string)
    while True:
        stdscr.refresh()
        i = stdscr.getch()
        if i == 8 or i == 127 or i == curses.KEY_BACKSPACE:
            input=input[:-1]
            stdscr.addstr('\b \b')
            continue
        for c in chars:
            if i is ord(c):
                if c is '\r' or c is '\n':
                    return input
                else:
                    input+=''+c
                    stdscr.addch(c)

def getMarixString(m):
    x = ''
    for row in m:
        x += ' '.join(str(item) for item in row)
        x += "\n"
    return x

def print_tbl(stdscr,t,tbl,lastch):
    if len(t) > 0:
        x=0
        il=0
        if ',' in tbl:
            spltbl=tbl.split(',')
            for i,key in enumerate(t.keys()):
                if il >= 6:
                    il=0
                    x+=1
                if spltbl[0] in key:
                    stdscr.addstr(x,il*5,key,curses.A_REVERSE)
                else:
                    stdscr.addstr(x,il*5,key)
                il+=1;
        else:
            for i,key in enumerate(t.keys()):
                if il >= 6:
                    il=0
                    x+=1
                if tbl in key:
                    stdscr.addstr(x,il*5,key,curses.A_REVERSE)
                else:
                    stdscr.addstr(x,il*5,key)
                il+=1;

        il=0
        xl=1
        x+=1
        if ',' in tbl:
            spltbl=tbl.split(',')
            for i,key in enumerate(t[spltbl[0]].keys()):
                if il >= 6:
                    il=0
                    x+=1
                if spltbl[1] in key:
                    stdscr.addstr(x,1+il*5,key,curses.A_REVERSE)
                else:
                    stdscr.addstr(x,1+il*5,key)
                il+=1;
        il=0
        xl=1
        if ',' in tbl:
            spltbl=tbl.split(',')
            for i,table in enumerate(t[spltbl[0]][spltbl[1]]):
                if il >= 6:
                    il=0
                    if xl == 7:
                        xl=0
                        x+=1
                    x+=1
                    xl+=1
                if lastch in table:
                    stdscr.addstr(2+x,2+(il*5),table,curses.A_REVERSE)
                else:
                    stdscr.addstr(2+x,2+(il*5),table)
                il+=1;
        else:
            for i,table in enumerate(t[tbl]):
                if il >= 6:
                    il=0
                    if xl == 7:
                        xl=0
                        x+=1
                    x+=1
                    xl+=1
                if lastch in table:
                    stdscr.addstr(2+x,1+(il*5),table,curses.A_REVERSE)
                else:
                    stdscr.addstr(2+x,1+(il*5),table)
                il+=1;

def main(stdscr):
    global ScreenH
    global ScreenW
    global CursorX
    global CursorY

    ScreenH, ScreenW = stdscr.getmaxyx()
    tables=None
    if os.path.isfile('tables.old.json'):
        with open('tables.old.json') as f:
            tables=json.loads(f.read())
    else:
        tables={'090':[]}
    stdscr.clear()
    choice=None
    lastch='99999'
    table='383'
    print_tbl(stdscr,tables,table,lastch)
    while True:
        choice=''
        choice = my_raw_input(stdscr, ScreenH-2, 0)
        choice = ''.join(choice.split())
        if choice is 'quit':
            break
        if choice is not '':
          if choice[0] is '-':
              if ',' in table:
                  splch=table.split(',')
                  if choice[1:] in tables[splch[0]][splch[1]]:
                      tables[splch[0]][splch[1]].remove(choice[1:])
                      lastch='99999'
              else:
                  if choice[1:] in tables[table]:
                      tables[table].remove(choice[1:])
                      lastch='99999'
              with open('tables.old.json', 'w') as outfile:
                  json.dump(tables, outfile)
          elif choice[0] is '/':
              if ',' in choice:
                  splch=choice[1:].split(',')
                  if not splch[0] in tables:
                      tables[splch[0]]={}
                  if not splch[1] in tables[splch[0]]:
                      tables[splch[0]][splch[1]]=[]
              else:
                  if not choice[1:] in tables:
                      tables[choice[1:]]=[]
              with open('tables.old.json', 'w') as outfile:
                  json.dump(tables, outfile)
              table=choice[1:]
              lastch='99999'
          else:
              if ',' in table:
                  spltbl=table.split(',')
                  if not choice in tables[spltbl[0]][spltbl[1]]:
                      tables[spltbl[0]][spltbl[1]].append(choice)
                      tables[spltbl[0]][spltbl[1]].sort()
              else:
                  if not choice in tables[table]:
                      tables[table].append(choice)
                      tables[table].sort()
              lastch=choice
              with open('tables.old.json', 'w') as outfile:
                  json.dump(tables, outfile)
              # tables.append('0x'+''.join('{:x}'.format(b) for b in choice.encode()))
          stdscr.clear()
          print_tbl(stdscr,tables,table,lastch)
    #if choice == "cool":
    #    stdscr.addstr(5,3,"Super cool!")
    #elif choice == "hot":
    #    stdscr.addstr(5, 3," HOT!")
    #else:
    #    stdscr.addstr(5, 3," Invalid input")
    stdscr.refresh()
    stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(main)

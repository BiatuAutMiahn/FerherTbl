#!/bin/bash
ttyd -p 13601 -t fontSize=16 -t fontFamily=inconsolata -t 'theme={"background":"black"}' /usr/bin/python3 /var/www/fehrertbl/tblmgr-dev.py

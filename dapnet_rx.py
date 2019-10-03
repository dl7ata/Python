#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Mitlesen Dapnet via Hamnet
# Bestandteil ist die Datei  rubrice.py  (s. Import)
# 02.10.2019    DL7ATA

import socket
import sys
import rubrice
from time import strftime

server = "44.225.164.27"
port = 43434

Counter = 0
LGREY = '\033[37m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
RED   = "\033[31m"
BLUE  = "\033[34m"
CYAN  = "\033[36m"
REVERSE = "\033[7m"

def Nachricht(RxString, Counter):
    MsgType = int(RxString[4:5])
    Baud = int(RxString[6:7])
    RIC = int(RxString[8:].split(":")[0], 16)
    Msg = RxString.split(":", 4)
    nachricht = Msg[4].rstrip()

    try:
        typ_RIC = rubrice.dic_RIC[str(RIC)]
        if RIC == 4520 or RIC == 4512:
            nachricht = ncode(nachricht[2:])
        print(strftime("%H:%M:%S"), Counter,
              GREEN, typ_RIC.ljust(18, ' '), ENDC, "\t", nachricht)
    except:
         typ_RIC =  str(RIC) + " RIC?"
         print(strftime("%H:%M:%S"), LGREY, Counter, typ_RIC.ljust(18, ' '), nachricht, ENDC)

def Auswertung(RxString, Counter):
    # print(RxString)
    suffix = RxString[:2]
    TxString = ''
    if suffix == "2:":
        TxString = "2:"+RxString[2:-1]+":0000\n+\n"
    elif suffix == "3:":
        TxString = "+\n"
    elif suffix == "4:":
        Slots = RxString[2:]
        print(Slots)
        TxString = "+\n"
    elif suffix[:1] == "#":
        MsgCount = int(RxString[1:3], 16)+1

        if MsgCount > 255:
            MsgCount = 0
        TxString = "#" + hex(MsgCount)[2:].zfill(2) + " +\n"
        Nachricht(RxString, Counter)
    else:
        print("Fehler")
    TxString = TxString.encode('utf-8')
    # print(TxString)
    s.sendall(TxString)
    return(Counter)

def ncode(data):
    newdata = ''
    key = -1
    for i in data:
        i = ord(i)
        if i + key >= 256:
            i = i - (256)
        newdata += chr(i+key)
    return newdata

print("Connecting to", server)
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

except socket.error:
    print("Fehler beim Connecten vom Server")
    sys.exit()

s.connect((server, port))

print("Connected!")
authkey = b'[AHKPager v0.3 db0tgo <password>]\n'

try:
    s.sendall(authkey)

except socket.error:
    print("Fehler beim Senden")
    sys.exit()

while True:
    reply = s.recv(4096).decode()
    # print(reply)
    Counter += 1
    if len(reply) > 0 and reply.endswith('\n'):
        Auswertung(reply, Counter)


#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Daten aus APRX
#   to-do!

import sys
import string
import os
import tailer
import aprslib
import requests
import time
from time import ctime

meinemsgid = "DL7ATA" # Sternchen und Minus nicht nötig mit anzugeben
passwd="21678"
res = ""

# Aufbereitung ack und Meldungsdatei erzeugen und kopieren
def ack_senden(absender,msgnummer):
    asc_nr = int(msgnummer)
    print("sende jetzt ACK {a:02d} aus".format(a=asc_nr))
    # ZIEL-CALL mit 9 Stellen indizieren und durch Zielcall ersetzten
    zielcall = [" "," "," "," "," "," "," "," "," "]
    for i in range(0,len(absender)):
        zielcall[i] = str(absender[i])

    # erzeugen der ack-MSg
    beacon_ack_buff =  ":" + ''.join(zielcall) + ":ack" + "{a:02d}".format(a=asc_nr)
    command = meinmsgid + ">APRS, TCPIP*:" + beacon_ack_buff + "\""

    # a valid passcode for the callsign is required in order to send
    AIS = aprslib.IS(meinmsgid, passwd, port=14580)
    AIS.connect()
    # senden ack-message
    AIS.sendall(command) #"N0CALL>APRS,TCPIP*:>status text")

    print(command)
    return

while True:
    for line in tailer.follow(open(logdatei)):
        text = ""
        for i in range(36,len(line)):
          text += str(line[i])

        try:
            decodiert = aprslib.parse(text)
            print(decodiert['from'], decodiert['format'], decodiert['raw'])
            if decodiert['format']=="message" and decodiert['addresse']==meinemsgid:
#            if decodiert['format']=="message" and decodiert['to']==meinemsgid and not decodiert['message_text'].find(":ack") >= 1:
                print(ctime(), decodiert['addresse'], decodiert['message_text'])
                ack_senden(decodiert['from'],str(decodiert['msgNo']))

             # Temp Datei erstellen und fuettern
                with open(dateiname, 'w+') as output:
                    zusendentext = "#" + decodiert['from'] + "#" + decodiert['addresse'] + "#" + decodiert['message_text'].replace(":","") + "#" + str(decodiert['msgNo'])
                    output.write(zusendentext)
                    output.close()

                print(ctime(), zusendentext)
                action_msg = "scp " + dateiname + " " + aprsmsgziel
                os.system(action_msg)

        except:
            #e = sys.exc_info()[0]
            pass

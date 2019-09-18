# !/usr/bin/python3
# -*- coding: utf-8 -*-
# APRSlib - Feld  Filtersetzung? Daher Port 10157/20157 mit Radius 100km
#
#             funtionstüchtig !

import aprslib
import geopy
from time import ctime

meinemsgid = "DL7ATA"
dateiname = "/tmp/APRS.msg"
a_format = "message"
aprs_host = "129.15.108.111"  # FIRST
aprs_port = 20158  # 100km

call = "DB0TGO-15"
# passwd="16571"
passwd = "-1"

print("Starte mit call " + call + " und port " +
      str(aprs_port) + ", Filter " + a_format)

def callback(packet):
    decodiert = aprslib.parse(packet)
    try:
        if decodiert['format'] == a_format:
            print(decodiert['raw'])
            print(ctime(), "\nVon: ", decodiert['from'],
                  " An: ", decodiert['addresse'],
                  "\033[31m", decodiert['message_text'],
                  "\033[0m.\n", decodiert['latitude'],
                  decodiert['longitude'])
    except KeyError:
        print('Error parsing, ein <ack> ... ?')
        pass

AIS = aprslib.IS(call, passwd, aprs_host, aprs_port)
AIS.connect()
AIS.consumer(callback, raw=True)
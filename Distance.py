# !/usr/bin/python3
# -*- coding: utf-8 -*-
# APRSlib - Feld  Filtersetzung? Daher Port 10157/20157 mit Radius 100km
#
#             funtionstüchtig !

import aprslib
from geopy import distance
from time import ctime

meinemsgid = "DL7ATA"
dateiname = "/tmp/APRS.msg"
a_format = "message"
aprs_host = "129.15.108.111"  # FIRST
aprs_port = 20157  # 100km
home = (52.5692293, 13.2312943)

call = "DB0TGO-15"
# passwd="16571"
passwd = "-1"

print("Starte mit call " + call + " und port " +
      str(aprs_port) + ", Filter " + a_format)

def callback(packet):
    decodiert = aprslib.parse(packet)
    try:
        stn = (decodiert['latitude'], decodiert['longitude'])
        print(decodiert['from'],
              round(distance.distance(home, stn).km, 1), "km")
    except KeyError:
        print('Error parsing, ein <ack> ... ?')
        pass

AIS = aprslib.IS(call, passwd, aprs_host, aprs_port)
AIS.connect()
AIS.consumer(callback, raw=True)
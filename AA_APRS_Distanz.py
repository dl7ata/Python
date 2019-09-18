#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 	FUNKTIoNSTÜCHTIG
# Mitlesen des APRSIS-Traffics von $filter

import socket
import sys
import time
import aprslib
from geopy import distance

filter = "m/100"    # "t/unq"   # TGO/DO5JRR/DB0AVH/DL2HAM\n" sys.argv[1]    #
aprsis_server="euro.aprs2.net"
port=14580
user = "DB0TGO-15"
home = (52.5692293, 13.2312943)

# APRS-Server IP auflösen
print("IP auflösen von " + aprsis_server)
host=socket.gethostbyname(aprsis_server)
print("Ho(r)st: " + host + ":" + str(port))

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.connect((host, port))
print("Verbunden mit " + host)

chunk = tcp.recv(4096).decode().rstrip()
print (chunk)
if chunk == b'':
    raise RuntimeError("socket connection broken")
else:
    print("Antwort:" + str(chunk))

    tx_text = ("user " + user + " " + "-1 vers Py7ATA V1.0 filter " +
               filter + "\n").encode('utf-8')
    tcp.sendall(tx_text)
    print(str(tx_text) + " gesendet....")
    chunk = tcp.recv(1024).decode().rstrip()
    print(time.strftime('%H:%M:%S'), chunk)

def callback(packet):
    try:
        decodiert = aprslib.parse(packet)
        stn = (decodiert['latitude'], decodiert['longitude'])
        print(time.strftime('%H:%M:%S'), decodiert['from'], "\t",
              round(distance.distance(home, stn).km, 1), "km")
    except(KeyError, UnicodeDecodeError, aprslib.ParseError, aprslib.UnknownFormat) as e:	# UnknownFormat("format is not supported")
         print("cant parse:", e, " mit ->", packet, "<-")
         pass

def main():
    while True:
        chunk = tcp.recv(4096).decode(errors='replace').rstrip()
        if not chunk[0] == "#":
            callback(chunk)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
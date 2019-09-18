#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 	FUNKTIoNSTÜCHTIG
# Mitlesen des APRSIS-Traffics von $filter

import socket
import sys
import time

filter="p/DB0TGO/DO5JRR/DB0AVH/DL2HAM"
aprsis_server="rotate.aprs2.net"
port=14580

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

tx_text=("user DB0TGO pass -1 vers Py7ATA V1.0 filter " + filter + "\n").encode('utf-8')
tcp.sendall(tx_text)
print(str(tx_text) + " gesendet....")

def main():
    while True:
        chunk = tcp.recv(4096).decode().rstrip()
        if not chunk[0] == "#":
            print (chunk)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# RSS-Feeds von $url einlesen und via DAPNET-http verteilen
# 30.10.2019    DL7ATA

import feedparser
import time
import hashlib
from pathlib import Path
import os

url = ['https://www.tagesspiegel.de/contentexport/feed/weltspiegel',
       'http://www.spiegel.de/schlagzeilen/tops/index.rss']
text_Pfad = "/tmp/aprs/rss."

counter = 0

def dapnet(zu_senden):
    bash_sc = '/bin/bash /home/svxlink/Scripte/Dapnet/dn_tx2.sh '
    cmd = bash_sc + '\'DL7ATA\'  \'DL2HAM\' ' \
        + "\'" + zu_senden + "\'"
    # cmd = bash_sc + 'DL7ATA ' + \
    #    "\"" +  zu_senden + "\""
    # print(cmd, len(zu_senden), "\n\n")
    os.system(cmd)
    time.sleep(5)

def zeilenumbruch(s, ll=71):
    if not len(s) > 71:
        dapnet(s)
        return
    aus = ""
    while len(s) > ll:
        p = ll-1
        while p > 0 and s[p] not in " ":
            p -= 1
        if p == 0:
            p = ll
        aus += s[:p+1]
        dapnet(aus)
        s = s[p+1:]
        dapnet(s[:p+1])

for i in url:

    f = feedparser.parse(i)
    msg = f["feed"]["title"]
    print(msg)

    for items in f["items"]:
        counter += 1
        title = items["title"]
        title = title.split(",")[0]

        hash_wert = hashlib.md5(title.encode())
        unikat = hash_wert.hexdigest()

        # prüfen ob Meldung schon vorhanden
        datei = text_Pfad + str(unikat)
        check_File = Path(datei)

        # Wenn Meldung noch nicht vorhanden
        if not check_File.is_file():
            title = title.replace("\"", "")
            with open(datei, 'w+') as output:
                    output.write(title)
                    output.close()
            print(time.strftime('%H:%M:%S'), title, "\n")
            zeilenumbruch(title, 71)

# löschen alter Meldungen (> 2 Tage)
cmd = 'find /tmp/aprs -name \'rss.*\' -mtime +2 -exec rm {} \\;'
os.system(cmd)

print(time.strftime('%H:%M:%S'), counter, "Nachrichten.")

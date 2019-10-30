#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# 08.10.2019	Anpassung an neues Modul "ModuleMowas.tcl" für svxlink
#
# Prüfen und ausgeben aktueller MOWAS-Meldungen für $Bundesland
# auf svxlink mit TTS 	06.10.2019	DL7ATA
#

import json
import requests
import sys
import re
import time
from datetime import datetime
import subprocess
import shutil

Bundesland1 = "NW"
Bundesland2 = "BB"

ident = 'identifier'
sent = 'sent'
ebene1 = 'msgType'
ebene2 = 'info'
ebene3 = 'headline'
ebene31 = 'description'
call = "DB0TGO"

url = 'https://warnung.bund.de/bbk.mowas/gefahrendurchsagen.json'

dateiname = "/tmp/aprsmsg.text"
mowas = 'MOWAS'
dst = 'DL7ATA'
z = 0
m = 0
msg_sammler = ''

def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

json_file = requests.get(url)
data = json_file.json()

for i in data[:]:
    ort = data[z][ident]
    von = data[z][sent]
    b_land = ort.split('-')[1]					# Bundesland
    meld_datum = von.split('T')[0]				# Meldungsdatum
    meld_zeit = von[11:19]					# Meldungszeit
    meld_zeit = meld_zeit.split(':')[0] + ":" + meld_zeit.split(':')[1]
    meld_datum = "vom " + \
                 datetime.strptime(meld_datum, '%Y-%m-%d').strftime('%d.%m.%Y')
    headline = data[z][ebene2][0][ebene3]			# Headline

    if b_land == Bundesland1 or b_land == Bundesland2:
        Meldung = cleanhtml(data[z][ebene2][0][ebene31])      # Meldungstext
        msg_sammler += meld_datum + ' um ' + \
            meld_zeit + ' Uhr: ' + headline + ". " + Meldung
        m += 1
    z += 1
    print(meld_datum, meld_zeit, b_land, headline)

print(time.strftime('%H:%M:%S'), " ", z,
      "Meldungen vorhanden,", m, "ausgegeben")

if m > 0:
    # WAV-Datei für svxlink erstellen
    spool_pfad = '/var/spool/svxlink/mowas/' + call + "." + ort + "."
    msg_text = 'Amtliche Warnung vom Bundesamt für \
                Bevölkerungsschutz und Katastrophenhilfe '\
                + msg_sammler

    try:
        subprocess.call(["/home/svxlink/TTS/tts.sh", msg_text, "m"])
    except(subprocess.SubprocessError) as e:
            print("Fehler bei Aufruf von tts.sh:", e)
            sys.exit(1)

    von = '/tmp/wx.wav'
    nach = spool_pfad + 'wav'
    shutil.copy2(von, nach)

    dateiname = spool_pfad + 'info'
    with open(dateiname, 'w+') as output:
        output.write(msg_text)
        output.close()
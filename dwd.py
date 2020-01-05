#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Einlesen eines dwd.unwetter - JSONs-Strings,
# filtern nach Regionen, Erstellung und Ausgabe einer WAV
#
# Version vom 05.01.2020
# Parsen nach Strings	16.10.2019	DL7ATA
#
# Diese Quelle listet erst höhere Kategorien wie Sturm und keine Winböen

import json
import sys, re, time
import requests
from json import loads
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

url = 'https://warnung.bund.de/bbk.dwd/unwetter.json'
text_Pfad = "/tmp/wx_msg/"
call = 'DB0TGO'

# 110000 00 bis
# 110000 12;Berlin - Reinickendorf;B-Reinickend.;BXH
# 112065 000;Kreis Oberhavel;Oberhavel;OHV	120650
# 112063 000;Kreis Havelland;Havelland;HVL
B1, B2, B3 = 110000, 120650, 120630

ident = 'identifier'
sent = 'sent'
ebene1 = 'msgType'
ebene2 = 'info'
ebene3 = 'headline'
ebene31 = 'description'
ebene30 = 'area'
ebene41 = 'areaDesc'
f_rot = '\033[31m'
f_gelb = '\033[33m'
f_aus = '\033[0m'
msg_sammler = ''

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, ' ', raw_html)
    return cleantext

def datum_drehen(datum):
    return(datetime.strptime(datum.split('T')[0],
           '%Y-%m-%d').strftime('%d.%m.%Y') + ", " + datum[11:16] +
           " Uhr")

if len(sys.argv) != 1:
    kurz = 1
else:
    kurz = 0

json_file = requests.get(url)
data = json_file.json()
z = 0
for i in data[:]:
    try:
        Nr = data[z][ident]						# Eineindeutige Nummer
        # Meldungszeit zusammenstellen
        von = datum_drehen(data[z]['info'][0]['effective'])
        ab = datum_drehen(data[z]['info'][0]['onset'])      		# gültig ab
        bis = datum_drehen(data[z]['info'][0]['expires'])

        headline = data[z][ebene2][0][ebene3]		                # headline
        # Meldungstext von HTML säubern
        Meldung = cleanhtml(data[z][ebene2][0][ebene31])

        z2 = 0
        gebiet = ''
        for j in data[z][ebene2][0][ebene30][:]:
            area = (data[z][ebene2][0][ebene30][z2][ebene41])
            area51 = data[z]['info'][0]['area'][z2]['geocode'][0]['valueName']
            geo_Code = "%.0f" % round(int(data[z]['info'][0]['area'][z2]['geocode'][0]['value'])/1000000, 0)
            z2 += 1
            # if geo_Code == B1 or geo_Code == B2 or geo_Code == B3:
            gebiet += "\n" + area + " " + area51 + " (#" + str(geo_Code) + ")/"

            # prüfen ob Meldung schon vorhanden
            datei = text_Pfad + Nr
            check_File = Path(datei)

            # Wenn Meldung noch nicht vorhanden und Bundesland gleich Auswahl
            if not check_File.is_file() and \
               (geo_Code == B1 or geo_Code == B2 or geo_Code == B3):
                msg_sammler += "Gültig von " + ab + ' bis ' + \
                    bis + ". " + headline + ". " + Meldung

                with open(datei, 'w+') as output:
                    output.write(msg_sammler)
                    output.close()
                print(time.strftime('%H:%M:%S'), "Datei ",
                      datei, " geschrieben")

                # WAV-Datei für svxlink erstellen
                print(time.strftime('%H:%M:%S'), " Erzeuge WAV")
                svx_spool_pfad = '/var/spool/svxlink/weatherinfo/'
                spool_pfad = svx_spool_pfad + call + "." + Nr + "."
                msg_text = 'Amtliche Warnung vom Deutschen Wetterdienst ' +\
                           msg_sammler
                try:
                    subprocess.call(["/home/svxlink/TTS/tts.sh",
                                     msg_text, "m"])
                    von = '/tmp/wx.wav'
                    # von tmp kopieren nach svx-spool als 70cm
                    nach = spool_pfad + 'wav'
                    # shutil.copy2(von, nach)
                    dateiname = spool_pfad + 'info-Text'
                    with open(dateiname, 'w+') as output:
                        output.write(msg_text)
                        output.close()
                    print(time.strftime('%H:%M:%S'), nach +
                          " erzeugt und kopiere.")

                    # kopieren nach svx-spool als 2m
                    nach = svx_spool_pfad + call + "-2m." + Nr + ".wav"
                    # shutil.copy2(von, nach)
                    nach = svx_spool_pfad + call + "-2m." + Nr + ".info"
                    # shutil.copy2(dateiname, nach)

                except(subprocess.SubprocessError) as e:
                    print(time.strftime('%H:%M:%S'),
                          "Fehler bei Aufruf von tts.sh:", e)
                    sys.exit(1)

    except KeyError as e:
            print("Fehler beim PARSEN von ", e, " in ", url)
            pass

    z += 1
    ausgabe = "\n" + headline + "\t gültig bis " + bis + "\t" + gebiet
    if kurz != 0:
        print(ausgabe, "\n" + f_gelb, Meldung, f_aus, "\n")
    else:
        print(ausgabe)

if kurz != 1:
    print(z, "Meldungen vorhanden.\n",
             "Kompletten Meldungstext ausgeben mit beliebigem Parameter")
else:
    print(z, "Meldungen vorhanden.")

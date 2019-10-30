#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# PARS-Fehler abfangen  29.10.2019
# einlesen dwd.unwetter und mowas - JSON-Strings
# 19.10.2019    DL7ATA

import json
import re
import requests
from datetime import datetime
import time

# schleifendauer
warten = 360

f_rot = '\033[31m'
f_gelb = '\033[33m'
f_aus = '\033[0m'
tabelle = []
url = ['https://warnung.bund.de/bbk.dwd/unwetter.json',
       'https://warnung.bund.de/bbk.mowas/gefahrendurchsagen.json',
       'https://warnung.bund.de/bbk.lhp/hochwassermeldungen.json',
       'https://warnung.bund.de/bbk.biwapp/warnmeldungen.json',
       'https://warnung.bund.de/bbk.katwarn/warnmeldungen.json']

def parsen():
    for j in url[:]:
        json_file = requests.get(j)
        data = json_file.json()
        z = 0
        quelle = j.split('/')[4].split('.')[0]
        for i in data[:]:
            # try:
                id = data[z]['identifier']
                # prüfen ob Meldung schon vorhanden
                if id not in tabelle[:]:
                    tabelle.append(id)
                    ausgabe = "Meldung " + id[:27].rstrip() + " vom "

                    # prüfen ob unwetter (64 Zeichen) oder Gefahrend. (< 30)
                    if len(id) > 50:
                        ab = datum_drehen(data[z]['info'][0]['effective'])  	# gültig ab
                        bis = datum_drehen(data[z]['info'][0]['expires'])  	# gültig bis
                    else:
                        b_land = id[:3]                     		# Bundesland bei mowas
                        ab = datum_drehen(data[z]['sent'])			# Datum gesendet

                    y = 0
                    gebiet = ''
                    for h in data[z]['info'][0]['area']:
                        area = \
                            (data[z]['info'][0]['area'][y]['areaDesc'])
                        # area51 = data[z]['info'][0]['area'][y]['geocode'][0]['valueName']
                        station = data[z]['info'][0]['area'][y]['geocode'][0]['value']
                        gebiet += area + "/"      # + station
                        y += 1

                    try:
                        Meldung = \
                            cleanhtml(data[z]['info'][0]['description']) 	# Meldungstext
                    except:
                        Meldung = ''
                        pass
                    headline = data[z]['info'][0]['headline']		# headline

                    ausgabe = time.strftime("%H:%M:%S") + " " + quelle + " Meldung " + \
                        id[:30].rstrip() + " vom " + ab + \
                        "\n" + gebiet + ":" + "\n" + f_gelb + headline + f_aus

                    print(ausgabe)     # print(ausgabe, f_gelb, Meldung, f_aus, "\n")

                z += 1

def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, ' ', raw_html)
    return cleantext

def datum_drehen(datum):
    return(datetime.strptime(datum.split('T')[0],
           '%Y-%m-%d').strftime('%d.%m.%Y') + ", " + datum[11:16] +
           " Uhr")
def main():
    counter = 0
    while True:
        i = warten
        counter += 1
        parsen()
        while i > 0:
            print(time.strftime("%H:%M:%S"),
                  " Durchlauf #", str(counter).rstrip(),
                  " Elemente #", len(tabelle), str(i).rstrip(), "   \r\b")
            i -= 1
            time.sleep(1)
main()

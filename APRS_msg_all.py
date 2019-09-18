#!/usr/bin/python3
# -*- coding: utf-8 -*-
# APRSlib - kein Feld  Filtersetzung vorhanden, daher Port 10158/20158 mit Radius 1000km
#

import aprslib
from time import strftime

meinemsgid="DL7ATA"
ata_passwd="****"
call="DB0TGO-15"
passwd="-1"

a_format="message"
aprs_host="129.15.108.111" #FIRST
aprs_port=20158 #1000km

# ack senden
def ack_senden(absender,msgnummer):
    asc_nr = int(msgnummer)
    print("Sende an ", absender, "  ACK {a:03d} aus".format(a=asc_nr))
    # ZIEL-CALL mit 9 Stellen indizieren und durch Zielcall ersetzten
    zielcall = [" "," "," "," "," "," "," "," "," "]
    for i in range(0,len(absender)):
        zielcall[i] = str(absender[i])

    # erzeugen der ack-MSg
    beacon_ack_buff =  ":" + ''.join(zielcall) + ":ack" + "{a:02d}".format(a=asc_nr)
    command = meinemsgid + ">APRS,TCPIP*:" + beacon_ack_buff #+ "\""
    # a valid passcode for the callsign is required in order to send
    AIS = aprslib.IS(meinemsgid, ata_passwd, port=14580)
    AIS.connect()
    # senden ack-message
    AIS.sendall(command)
    print("Gesendet: ", command, "\n")
    return

def callback(packet):
    decodiert = aprslib.parse(packet)
    try:
        if decodiert['format']==a_format:
            print(strftime("%H:%M:%S"), "Von: ", decodiert['from'], " An: ", decodiert['addresse'], "\033[31m", decodiert['message_text'], "\033[0m.")
            print("RAW: ",decodiert['raw'])
            if decodiert['addresse']==meinemsgid and not decodiert['message_text'].find(":ack") >= 1:
#                print("Sende ACK an ", decodiert['from'])
                ack_senden(decodiert['from'],str(decodiert['msgNo']))
    except KeyError:
        print ('Wohl ein <ack> ... ?')
        print(decodiert['raw'])
        pass

def main():
    while True:
        AIS = aprslib.IS(call, passwd, aprs_host, aprs_port)
        AIS.connect()
        # by default `raw` is False, then each line is ran through aprslib.parse()
        AIS.consumer(callback, raw=True)

print ("Starte mit Rufzeichen " + call + " und Ziel "+aprs_host + ":" + str(aprs_port) + ", Filter " + a_format + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass

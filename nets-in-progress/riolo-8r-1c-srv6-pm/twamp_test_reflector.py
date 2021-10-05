#!/usr/bin/python3

from scapy.all import *
from scapy.layers.inet import IP,UDP
from scapy.layers.inet6 import IPv6

import twamp
import twamp_dM

# segment list file (file esempio con 2 segmenti)
seg_file = open("SRv6-List", "r")
seg_list = seg_file.read().splitlines() # suppose symmetric path for sender and reflector
seg_file.close
# ho la lista dei segmenti per il momento
# immagino di avere un db con SSID|SegList in cui tramite il SSID
# seleziono la seglist corrispondente
# (src e dst IP + src e dst UDP --> SSID)


reflector = twamp_dM.Reflector(seg_list)
t_dm = twamp_dM.TWAMPDelayMeasurement(reflector=reflector)


t_dm.start()

#!/usr/bin/python3
from scapy.all import *
from scapy.layers.inet import IP,UDP

from scapy.layers.inet6 import IPv6
import twamp
import twamp_dM
import time


reflector_file = open("IPv6-Reflector", "r")
dst_addr = reflector_file.readline().split('\n')[0]
reflector_file.close

# segment list file (file esempio con 2 segmenti)
seg_file = open("SRv6-List", "r")
seg_list = seg_file.read().splitlines() 
seg_file.close
# ho la lista dei segmenti per il momento, 
# immagino di avere un db con SSID|SegList in cui tramite il SSID
# seleziono la seglist relativa
# (src e dst IP + src e dst UDP --> SSID)

sender = twamp_dM.Sender(dst_addr, seg_list) # segment list added to Sender class

t_dm = twamp_dM.TWAMPDelayMeasurement(sender=sender)


t_dm.start()

time.sleep(2)
sender.sendSenderDelayPacket() 


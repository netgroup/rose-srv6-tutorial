
from scapy.all import *
from scapy.layers.inet import IP, UDP

from scapy.layers.inet6 import IPv6
import twamp
import twamp_dM
import time


reflector_file = open("IPv6-Reflector", "r")
dst_addr = reflector_file.readline().split('\n')[0]

sender = twamp_dM.Sender(dst_addr)
t_dm = twamp_dM.TWAMPDelayMeasurement(sender=sender)


t_dm.start()

time.sleep(2)
sender.sendSenderDelayPacket()

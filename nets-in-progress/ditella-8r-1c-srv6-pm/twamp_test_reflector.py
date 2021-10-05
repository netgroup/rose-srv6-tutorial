#!/usr/bin/python

from scapy.all import *
from scapy.layers.inet import IP,UDP
from scapy.layers.inet6 import IPv6

import twamp
import twamp_dM


reflector = twamp_dM.Reflector()
t_dm = twamp_dM.TWAMPDelayMeasurement(reflector=reflector)


t_dm.start()
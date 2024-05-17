#!/usr/bin/python3
from scapy.all import *


class TWAMPTPacketSender(Packet):
    name = "TWAMPPacketSender"
    fields_desc = [IntField("SequenceNumber", 0),
                   BitField("FirstPartTimestamp", 0, 32),
                   BitField("SecondPartTimestamp", 0, 32),
                   BitEnumField("S", 0, 1, {0: " no external synchronization",
                                            1: "external synchronization"}),
                   BitField("Z", 0, 1),
                   BitField("Scale", 0, 6),
                   BitField("Multiplier", 1, 8)]  # manca il padding


class TWAMPTPacketReflector(Packet):
    name = "TWAMPPacketReflector"
    fields_desc = [IntField("SequenceNumber", 0),
                   BitField("FirstPartTimestamp", 0, 32),
                   BitField("SecondPartTimestamp", 0, 32),
                   BitEnumField("S", 0, 1, {0: " no external synchronization",
                                            1: "external synchronization"}),
                   BitField("Z", 0, 1),
                   BitField("Scale", 0, 6),
                   BitField("Multiplier", 1, 8),
                   BitField("MBZ", 0, 16),
                   BitField("FirstPartTimestampReceiver", 0, 32),
                   BitField("SecondPartTimestampReceiver", 0, 32),
                   IntField("SequenceNumberSender", 0),
                   BitField("FirstPartTimestampSender", 0, 32),
                   BitField("SecondPartTimestampSender", 0, 32),
                   BitEnumField("SSender", 0, 1, {0: " no external synchronization",
                                                  1: "external synchronization"}),
                   BitField("ZSender ", 0, 1),
                   BitField("ScaleSender", 0, 6),
                   BitField("MultiplierSender", 1, 8),
                   BitField("MBZ", 0, 16),
                   ByteField("SenderTTL", 255)]  # manca il padding

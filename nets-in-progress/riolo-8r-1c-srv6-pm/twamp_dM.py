from scapy.all import *
from scapy.layers.inet import IP, UDP
from scapy.layers.inet6 import IPv6
import twamp
from datetime import datetime
from threading import Thread
import time
import netifaces
import struct


# Constants to convert between python timestamps and NTP 8B binary format
# [RFC1305]
TIMEOFFSET = int(2208988800)    # Time Difference: 1-JAN-1900 to 1-JAN-1970
ALLBITS = int(0xFFFFFFFF)       # To calculate 32bit fraction of the second

# Number of packet exchanged between sender and reflector, modify to your
# choice
MAXPACKETSENT = int(500)


class TWAMPDelayMeasurement(Thread):

    def __init__(self, interface=get_if_list(), sender=None, reflector=None):

        Thread.__init__(self)
        self.interface = interface
        self.SessionSender = sender
        self.SessionReflector = reflector
        self.maxPacketSent = MAXPACKETSENT

        # If a specific interface is used, extract its IPv6 addr
        if(isinstance(interface, type('string'))):
            addrs = netifaces.ifaddresses(interface)
            ipv6_addr = addrs[netifaces.AF_INET6][0]['addr']

        # If no interface is used, use global IPv6 addr
        else:
            addrs = netifaces.ifaddresses('lo')
            ipv6_addr = addrs[netifaces.AF_INET6][0]['addr']

        # setting ipv6 address according to the choosen interface
        if(self.SessionReflector is None):
            self.SessionSender.srcAddr = ipv6_addr
            print('Sono il sender')

        else:
            self.SessionReflector.srcAddr = ipv6_addr
            print('Sono il reflector')

    def packetRecvCallback(self, packet):

        if UDP in packet:
            if packet[UDP].dport == 20001:
                packet[UDP].decode_payload_as(twamp.TWAMPTPacketSender)

                if(self.SessionReflector is not None):
                    self.SessionReflector.recvTWAMPfromSender(packet)

            elif packet[UDP].dport == 20000:
                packet[UDP].decode_payload_as(twamp.TWAMPTPacketReflector)

                if(self.SessionSender is not None):
                    self.SessionSender.recvTWAMPfromReflector(packet)

    # sniff stop filter

    def stopfilter(self, packet):
        if packet[UDP].SequenceNumber == self.maxPacketSent - 1:
            return True
        else:
            return False

    def run(self):

        print("TestPacketReceiver Start sniffing...")
        sniff(
            iface=self.interface,
            filter="udp",
            prn=self.packetRecvCallback,
            stop_filter=self.stopfilter)  # changed filter to UDP
        print("TestPacketReceiver Stop sniffing")


class TWAMPUtils():

    def __init__(self):
        print("Util class")

    def getTimestamp(self):

        t = datetime.timestamp(datetime.now()) + TIMEOFFSET

        # 32bit fraction of the second
        floatTimestamp = int((t - int(t)) * ALLBITS)

        intTimestamp = int(t)

        return (intTimestamp, floatTimestamp)


class Reflector(TWAMPUtils):

    def __init__(self, segList):  # added segList

        # set to its superclass constructor
        self.srcAddr = ''
        self.senderSequenceNumber = 0
        self.senderTSint = 0
        self.senderTSfloat = 0
        self.segList = segList  # added segment list
        self.maxPacketSent = MAXPACKETSENT

    """
            This method is used upon receiving a packet from a sender.
            The method send a reply to the sender according to TWAMP standard
        """

    def sendReflectorDelayPacket(
            self,
            dstAddr,
            sequence_number,
            scale=0,
            multiplier=1,
            mBZ=0,
            SSender=0,
            ZSender=0,
            scaleSender=0,
            multiplierSender=1):

        timestamp = self.getTimestamp()

        ipv6_packet = IPv6()
        ipv6_packet.src = self.srcAddr
        ipv6_packet.dst = self.segList[-1]  # last list's segment

        # srv6 header added
        srv6_header = IPv6ExtHdrSegmentRouting()
        srv6_header.addresses = self.segList  # no necessary to reverse for reflector
        srv6_header.segleft = len(self.segList) - 1  # -1 because start from 0
        srv6_header.lastentry = len(self.segList) - 1

        ipv6_packet_inside = IPv6()
        # src ipv6 inner (reflector's addr)
        ipv6_packet_inside.src = self.srcAddr
        ipv6_packet_inside.dst = dstAddr  # dst ipv6 inner (sender's addr)

        udp_packet = UDP()
        udp_packet.dport = 20000
        udp_packet.sport = 20001

        twamp_reflector = twamp.TWAMPTPacketReflector(
            SequenceNumber=sequence_number,
            FirstPartTimestamp=timestamp[0],
            SecondPartTimestamp=timestamp[1],
            Scale=scale,
            Multiplier=multiplier,
            MBZ=mBZ,
            FirstPartTimestampReceiver=timestamp[0],
            SecondPartTimestampReceiver=timestamp[1],
            SequenceNumberSender=self.senderSequenceNumber,
            FirstPartTimestampSender=self.senderTSint,
            SecondPartTimestampSender=self.senderTSfloat,
            ScaleSender=scaleSender,
            MultiplierSender=multiplierSender)
        pkt = (
            ipv6_packet /
            srv6_header /
            ipv6_packet_inside /
            udp_packet /
            twamp_reflector)

        send(pkt, verbose=1)

    """
            Methods triggered when received a packet from (TWAMP) sender.
            This method extract the needed field to be used to craft the corresponding reply.
        """

    def recvTWAMPfromSender(self, packet):

        self.srcAddr = packet[IPv6].dst
        dstAddr = packet[IPv6].src

        packet[UDP].decode_payload_as(twamp.TWAMPTPacketSender)

        sequence_number = packet[UDP].SequenceNumber

        self.senderSequenceNumber = packet[UDP].SequenceNumber
        self.senderTSint = packet[UDP].FirstPartTimestamp
        self.senderTSfloat = packet[UDP].SecondPartTimestamp

        self.sendReflectorDelayPacket(
            sequence_number=sequence_number, dstAddr=dstAddr)


class Sender(TWAMPUtils):

    def __init__(self, dstAddr, segList):

        # set to its superclass constructor
        self.srcAddr = ''
        self.dstAddr = dstAddr
        self.segList = segList  # add segment List

        self.SequenceNumber = 0
        self.avarageDelayMeasured = 0.0
        self.maxPacketSent = MAXPACKETSENT   # modificato per provare (era 500)
        self.revSegList = segList[::-1]  # segList reversed

    def sendSenderDelayPacket(self, scale=0, multiplier=1):

        timestamp = self.getTimestamp()

        ipv6_packet = IPv6()
        ipv6_packet.src = self.srcAddr
        ipv6_packet.dst = self.segList[0]  # primo segmento dst ipv6 outer

        # TODO parte Srv6 qui

        srv6_header = IPv6ExtHdrSegmentRouting()
        # reversed order of segList in srv6 header
        srv6_header.addresses = self.revSegList
        srv6_header.segleft = len(self.revSegList) - \
            1  # -1 beacuse start from 0
        srv6_header.lastentry = len(self.revSegList) - 1

        ipv6_packet_inside = IPv6()
        ipv6_packet_inside.src = self.srcAddr  # src ipv6 inner (sender's addr)
        # dst ipv6 inner (reflector's addr)
        ipv6_packet_inside.dst = self.dstAddr

        #########

        udp_packet = UDP()
        udp_packet.dport = 20001
        udp_packet.sport = 20000

        twampPaylod = twamp.TWAMPTPacketSender(
            SequenceNumber=self.SequenceNumber,
            FirstPartTimestamp=timestamp[0],
            SecondPartTimestamp=timestamp[1],
            Scale=scale,
            Multiplier=multiplier)

        pkt = (ipv6_packet / srv6_header / ipv6_packet_inside /
               udp_packet / twampPaylod)  # new pkt with srv6 header

        send(pkt, verbose=1)

    """
        Method triggered on receiving a reply from the reflector.
        This method extracts the fields of the packet received from the reflector
        in order to evaluate the avatage delay.
    """

    def recvTWAMPfromReflector(self, packet):

        packet[UDP].decode_payload_as(twamp.TWAMPTPacketReflector)

        if (packet[UDP].SequenceNumber == self.SequenceNumber):

            delay = (packet[UDP].FirstPartTimestampReceiver + float("0.%d" %
                                                                    packet[UDP].SecondPartTimestampReceiver)) - (packet[UDP].FirstPartTimestampSender + float("0.%d" %
                                                                                                                                                              packet[UDP].SecondPartTimestampSender))

            # Welford Online Algorithm for avarage evaluation
            self.avarageDelayMeasured = float(self.avarageDelayMeasured) + (
                delay - self.avarageDelayMeasured) / float(self.SequenceNumber + 1)

            if (self.maxPacketSent == self.SequenceNumber + 1):
                self.showPacketDelay()
                return
            else:
                self.SequenceNumber = packet[UDP].SequenceNumber + 1
                self.sendSenderDelayPacket()

        else:
            # pacchetto scartato
            return

    # Method called automatically when the time delay measurement has finished
    def showPacketDelay(self):
        print("After sending {} packets, the measured delay is: {} seconds".format(
            self.maxPacketSent, self.avarageDelayMeasured))

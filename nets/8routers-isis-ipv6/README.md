# 1920-srv6-tutorial
```
SMART INTRODUCTION LINK ---> https://drive.google.com/file/d/18PumHFw6o3df5-_yPtOVw4Zem8RDEjTr/view?usp=sharing
```
<<<<<<< HEAD
Python program isi8d.py creates network and opens mininet
=======
Python program isi8d.py creates network and opens mininet
>>>>>>> d23c758232730ca9dc916ee143384b3f17c75abc
In folder nodeconf/ 
	- for each host and router one folder
	- host folders contain start.sh for each host
		- sets IPv6 address for hosts
		- adds IPv6 routing to gateway
	- router folders contain 
		- zebra.conf
			- sets for each interface the IPv6 address
		- isisd.conf
			- contains routing information
		- start.sh
			- enables IPv6 forwarding
<<<<<<< HEAD
			- executes zebra.conf and isisd.conf
=======
			- executes zebra.conf and isis8d.conf
>>>>>>> d23c758232730ca9dc916ee143384b3f17c75abc
```

network:
the network is shown in this link
https://drive.google.com/file/d/1yzyfgvgWbzPjTttcqA4G41gEGM87tHC5/view?usp=sharing

host - router links:

	h11 - r1: fd00:0:11::2/64	r1 - h11: fd00:0:11::1/64
	h12 - r1: fd00:0:12::2/64	r1 - h12: fd00:0:12::1/64
	h13 - r1: fd00:0:13::2/64	r1 - h13: fd00:0:13::1/64

	h31 - r3: fd00:0:31::2/64	r3 - h31: fd00:0:31::1/64
	h32 - r3: fd00:0:32::2/64	r3 - h32: fd00:0:32::1/64
	h33 - r3: fd00:0:33::2/64	r3 - h33: fd00:0:33::1/64

	h51 - r5: fd00:0:51::2/64	r5 - h51: fd00:0:51::1/64
	h52 - r5: fd00:0:52::2/64	r5 - h52: fd00:0:52::1/64
	h53 - r5: fd00:0:53::2/64	r5 - h53: fd00:0:53::1/64

	h81 - r8: fd00:0:81::2/64	r8 - h81: fd00:0:81::1/64
	h82 - r8: fd00:0:82::2/64	r8 - h82: fd00:0:82::1/64
	h83 - r8: fd00:0:83::2/64	r8 - h83: fd00:0:83::1/64

router - router links:
	
	r1 -r2: fcf0:0:1:2::1/64	r2 - r1: fcf0:0:1:2::2/64
	r2 -r3: fcf0:0:2:3::1/64	r3 - r2: fcf0:0:2:3::2/64
	r2 -r7: fcf0:0:2:7::1/64	r7 - r2: fcf0:0:2:7::2/64
	r3 -r4: fcf0:0:3:4::1/64	r4 - r3: fcf0:0:3:4::2/64
	r4 -r5: fcf0:0:4:5::1/64	r5 - r4: fcf0:0:4:5::2/64
	r4 -r6: fcf0:0:4:6::1/64	r6 - r4: fcf0:0:4:6::2/64
	r5 -r6: fcf0:0:5:6::1/64	r6 - r5: fcf0:0:5:6::2/64
	r6 -r7: fcf0:0:6:7::1/64	r7 - r6: fcf0:0:6:7::2/64
	r6 -r8: fcf0:0:6:8::1/64	r8 - r6: fcf0:0:6:8::2/64
	r7 -r8: fcf0:0:7:8::1/64	r8 - r7: fcf0:0:7:8::2/64

( The addressing plan is explained in https://docs.google.com/document/d/15giV53fH_eDuWadOxzjPVzlr-a7Rn65MpCbz9QKs7JI/edit )

------ISIS CONFIGURATION-------------

Install guide and How to get FRR

The official FRR website is located at https://frrouting.org/ and contains further information, as well as links to additional resources.

Several distributions provide packages for FRR. Check your distribution’s repositories to find out if a suitable version is available.

Daemons Configuration File

After a fresh install, starting FRR will do nothing. This is because daemons must be explicitly enabled by editing a file in your configuration directory. This file is usually located at /etc/frr/ daemons and determines which daemons are activated when issuing a service start / stop command via init or systemd. The file initially looks like this:

zebra=no
bgpd=no
ospfd=no
ospf6d=no
ripd=no
ripngd=no
isisd=yes
pimd=no
ldpd=no
nhrpd=no
eigrpd=no
babeld=no
sharpd=no
staticd=no
pbrd=no
bfdd=no
fabricd=no

....

We have to enable the deamon, so modify the word "isis=no" with "isisd=yes"


----ISIS Configuration----

Common options can be specified (Common Invocation Options) to isisd. isisd needs to acquire interface information from zebra in order to function. Therefore zebra must be running before invoking isisd. Also, if zebra is restarted then isisd must be too.


Each routers contains the files "isisd.conf" "start.sh" "zebra.conf"


The configuration of "zebra.conf" of each routers is for example:
!
hostname r1
log file nodeconf/r1/zebra.log
!
debug zebra events
debug zebra rib
!
interface r1-h11
 ipv6 address fd00:0:11::1/64
!
interface r1-h12
 ipv6 address fd00:0:12::1/64
!
interface r1-h13
 ipv6 address fd00:0:13::1/64
!
interface r1-r2
 ipv6 address fcf0:0:1:2::1/64
!
interface lo
 ipv6 address fcff:1::1/128
!
ipv6 forwarding
!
line vty
!


In this file we define the interface between the links of router r1 and the hosts that are linked, in particular we also define the interface "lo" of the router 
With the command "ipv6 forwarding" we explicitly enable the ipv6 forwarding



The configuration of "isisd.conf" of each routers is for example:

hostname rx
password XXXX
log file nodeconf/r1/isisd.log
!
interface lo
 ipv6 router isis XX
 ip router isis XX
 isis hello-interval 5
!
interface r1-h1 
 ipv6 router isis XX
 ip router isis XX
 isis hello-interval 5
!
interface r1-r2 
 ipv6 router isis XX
 ip router isis XX
 isis hello-interval 5
!
interface r1-r3
 ipv6 router isis XX
 ip router isis XX
 isis hello-interval 5
!
router isis XX
  net 49.000X.XXXX.XXXX.XXXX.00
  is-type level-2-only
  metric-style wide
!
line vty

we use the command "ipv6 router isis XX" to use ipv6
the command "isis hello-interval (1-600)
" configure the level 1 hello interval

The command
net XX.XXXX. ... .XXX.XX
Set/Unset network entity title (NET) provided in ISO format.
NETs take several forms, depending on your network requirements. NET addresses are hexadecimal and range from 8 octets to 20 octets in length. Generally, the format consists of an authority and format Identifier (AFI), a domain ID, an area ID, a system identifier, and a selector. The simplest format omits the domain ID and is 10 octets long. For example, the NET address 49.0001.1921.6800.1001.00 consists of the following parts:

49—AFI
0001—Area ID
1921.6800.1001—System identifier
00—Selector

The system identifier must be unique within the network.
The first portion of the address is the area number, which is a variable number from 1 through 13 bytes. The first byte of the area number (49) is the authority and format indicator (AFI). The next bytes are the assigned domain (area) identifier, which can be from 0 through 12 bytes. In the examples above, the area identifier is 0001.
The next six bytes form the system identifier. The system identifier can be any six bytes that are unique throughout the entire domain. The system identifier commonly is the media access control (MAC) address.
The last byte (00) is the n-selector.



The command
  is-type level-2-only

Level 1 systems route within an area; when the destination is outside an area, they route toward a Level 2 system. Level 2 intermediate systems route between areas and toward other ASs. No IS-IS area functions strictly as a backbone.
Level 1 routers share intra-area routing information, and Level 2 routers share interarea information about IP addresses available within each area. Uniquely, IS-IS routers can act as both Level 1 and Level 2 routers, sharing intra-area routes with other Level 1 routers and interarea routes with other Level 2 routers.

We can choose level 1 or level 2, but its a good idea use level 2 beacause we can route packet out of the networks

----Configuration of Hosts----

each host has a configuration file called start.sh
Currently IPv6 forwarding is not explicitly enabled in start.sh, we have to configure ipv6 addresses for each hosts

Example of configuration of start.sh

BASE_DIR=/home/user/Progetto/1920-srv6-tutorial/nets/8routers-isis-ipv6/nodeconf
NODE_NAME=h11
GW_NAME=r1
IF_NAME=$NODE_NAME-$GW_NAME
IP_ADDR=fd00:0:11::2/64
GW_ADDR=fd00:0:11::1

ip -6 addr add $IP_ADDR dev $IF_NAME 
ip -6 route add default via $GW_ADDR dev $IF_NAME

----Addressing----

the addressing on the links between the hosts hxy and the router x can be
Router interface rx-hxy fd00:0:xy::1/64
Host interface hxy-ry fd00:0:xy::2/64

```
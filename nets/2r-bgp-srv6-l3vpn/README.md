# 2r-bgp-srv6-l3vpn/ Topology

A Mininet topology with 8 routers running IS-IS routing protocol and 6 hosts.


```text

In folder nodeconf/ 
	- for each host, datacenter and router one folder
	- host folders contain start.sh for each host
		- sets IPv6 address for hosts
		- adds IPv6 routing to gateway
	- router folders contain 
		- zebra.conf
			- sets for each interface the IPv6 address
		- staticd.conf
		    - sets the routes required for SRv6
		- bgpd.conf
			- sets BGP and VPN parameters
		- start.sh
			- enables IPv6 forwarding
			- executes zebra, staticd and bgp





host - router links:

	h11 - pe1: fd00:0:11::2/64	pe1 - h11: fd00:0:11::1/64
	h12 - pe1: fd00:0:12::2/64	pe1 - h12: fd00:0:12::1/64
	h13 - pe1: fd00:0:13::2/64	pe1 - h13: fd00:0:13::1/64

	h21 - pe2: fd00:0:21::2/64	pe2 - h21: fd00:0:21::1/64
	h22 - pe2: fd00:0:22::2/64	pe2 - h22: fd00:0:22::1/64
	h23 - pe2: fd00:0:23::2/64	pe2 - h23: fd00:0:23::1/64

router - router links:
	
	pe1 -pe2: fcf0:0:1:2::1/64	pe2 - pe1: fcf0:0:1:2::2/64
	
router localhost

    r1 fcff:1::1
    r2 fcff:2::1

( The addressing plan is explained in https://docs.google.com/document/d/15giV53fH_eDuWadOxzjPVzlr-a7Rn65MpCbz9QKs7JI/edit )


The file etc-hosts in the topology folder maps each IP address to its hostname.

For example,
fcff:1::1       pe1
fd00:0:11::2    h11
...

When you start the topology, the entries defined in this file are loaded and added to the system /etc/hosts file.

This allows you to ping the nodes using their hostnames instead of the IP addresses:
h11# ping6 h21
h21# ping6 h11

The entries are automatically removed from the /etc/hosts file when the emulation is stopped.

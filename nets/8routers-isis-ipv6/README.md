# 1920-srv6-tutorial

project description and discussion: 
https://docs.google.com/document/d/1I3Aj1HdJky4Mcy-eiNSsFkcV3nars7q7SOyohabsLgc/edit

```
Python program isis8d.py creates network and opens mininet
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
			- executes zebra.conf and isisd.conf
```

network:
the network is shown in this link
https://docs.google.com/presentation/d/15w14n_Nf5rE560FluMnw4Wq51pYLvDqG1kEwDvmEHE0/edit#slide=id.g76160fda07_0_0

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
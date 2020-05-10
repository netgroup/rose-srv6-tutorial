# SRv6 tutorial

In the nets folder there are different projects:

```
- 3routers
small IPv4 topology with OSPF / FRR

- 8routers
reference IPv6 topology with OSPFv3 / FRR

- 8routers-isis-ipv6
reference IPv6 topology with IS-IS / FRR

- 8r-1c-out-band-isis
reference IPv6 topology with IS-IS / FRR and out-of-band controller

- 8r-1c-in-band-isis
reference IPv6 topology with IS-IS / FRR and in-band controller

```

## Installation of FRRouting suite (FRR)

You need to have FRR installed in order to run the mininet labs.
Check if FRR is installed by running:
```
  
  /usr/lib/frr/zebra -v
```

If FRR is not installed, follow these instructions (for Ubuntu/Debian): 

1) wget https://deb.frrouting.org/frr/keys.asc

2) sudo apt-key add keys.asc

3) rm keys.asc

4) run lsb_release -s -c

5) Edit the sources.list file in the /etc/apt folder, adding the following line at the end:
```

deb https://deb.frrouting.org/frr <release> frr-stable	
```
replacing <release> with the output of lsb_release -s -c 

6) sudo apt update

7) sudo apt -y install frr frr-pythontools



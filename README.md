# SRv6 tutorial

In the nets folder there are different projects:

```
- 3routers
small IPv4 topology with OSPF / FRR

- 8routers
reference IPv6 topology with OSPFv3 / FRR

- 3routers-isis-ipv6
small IPv6 topology with IS-IS / FRR

- 8routers-isis-ipv6
reference IPv6 topology with IS-IS / FRR

- YAML
IPv6 topology can be defined, dynamic routing with OSPFv3 / FRR

```

## Installation of FRRouting suite (FRR)

You need to have FRR installed in order to run the mininet labs.
Check if FRR is installed by running:
```
  
  /usr/lib/frr/zebra -v
```

For the installation on Ubuntu, simply run:
```    

  sudo snap install frr
```
as described in https://snapcraft.io/install/frr/ubuntu

Installation from source code is described here: http://docs.frrouting.org/en/latest/installation.html#from-source



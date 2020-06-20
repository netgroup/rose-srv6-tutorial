# SRv6 tutorial

> Mininet topologies for SRv6

![Python Linter](https://github.com/netgroup/rose-srv6-tutorial/workflows/Python%20Linter/badge.svg)
![Shell Linter](https://github.com/netgroup/rose-srv6-tutorial/workflows/Shell%20Linter/badge.svg)
![Python package](https://github.com/netgroup/rose-srv6-tutorial/workflows/Python%20package/badge.svg)
![GitHub](https://img.shields.io/github/license/netgroup/rose-srv6-control-plane)

## Table of Contents
* [Overview](#overview)
* [Installation](#installation)
    * [Installation of Mininet](#installation-of-mininet)
    * [Installation of FRRouting suite (FRR)](#installation-of-frrouting-suite-frr)
    * [Installation of Python dependencies](#installation-of-python-dependencies)
* [Starting a topology](#starting-a-topology)
* [Requirements](#requirements)
* [Links](#links)
* [Issues](#issues)
* [Contributing](#contributing)
* [License](#license)

## Overview

This project contains several Mininet topologies:

    .
    ├── nets
    |   ├── 8routers-isis-ipv6
    |   └── 8r-1c-in-band-isis
    ├── nets-in-progress
    |   └── 8r-1c-srv6-pm
    ├── nets-unmantained
    |   ├── 3routers
    |   ├── 8routers
    |   └── 8r-1c-out-band-isis
    └── README.md

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

- 8r-1c-srv6-pm
reference IPv6 topology with IS-IS / FRR and out-of-band controller, used for SRv6 Performance Measurement experiments

```

## Installation

This project depends on:
  * Mininet
  * FRRouting suite
  * Other Python packages listed in requirements.txt

### Installation of Mininet

Check if Mininet is installed by running:
```
$ /usr/bin/mn --version
```

If Mininet is not installed, run the install command (for Ubuntu/Debian):
```
$ sudo apt-get install mininet
```

### Installation of FRRouting suite (FRR)

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

### Installation of Python dependencies

The Python packages required to run the Mininet labs are listed in *requirements.txt*. You can install them with the following command:
```
$ pip install -r requirements.txt
```


## Starting a topology

In order to start a Mininet topology `cd` to the topology folder and run the Python script.

For instance,
```
$ cd nets/8routers-isis-ipv6/
$ python isis8d.py
```

For more information, check the documentation contained in the topology folders.


## Requirements
Python >= 3.6


## Links
* Research on Open SRv6 Ecosystem (ROSE): https://netgroup.github.io/rose/
* Source code: https://github.com/netgroup/rose-srv6-tutorial
* Report a bug: https://github.com/netgroup/rose-srv6-tutorial/issues


## Issues
You are welcome to open github issues for bug reports and feature requests, in [this repository](https://github.com/netgroup/rose-srv6-tutorial/issues) or in the [ROSE repository](https://github.com/netgroup/rose/issues).


## Contributing
If you want to contribute to the ecosystem, provide feedback or get in touch with us, see our contact page: https://netgroup.github.io/rose/rose-contacts.html.


## License
This project is licensed under the [Apache License, Version 2.0](https://github.com/netgroup/rose-srv6-tutorial/blob/master/LICENSE).

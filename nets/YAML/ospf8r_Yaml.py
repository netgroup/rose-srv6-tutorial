#!/usr/bin/python
# coding=utf-8

import os
import shutil
import yaml
import argparse
import sys
from mininet.topo import Topo
from mininet.node import Host
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.util import dumpNodeConnections
from mininet.link import Link
from mininet.log import setLogLevel
from mininet.link import TCLink

#remove directory nodeconf/
if os.path.exists("nodeconf"):
    shutil.rmtree("nodeconf")

#BASEDIR = "/home/user/mytests/ospf8routers/nodeconf/"
BASEDIR = os.getcwd()+"/nodeconf/"
OUTPUT_PID_TABLE_FILE = "/tmp/pid_table_file.txt"

PRIVDIR = '/var/priv'

#variable declaration
router_name = {}
router_id = {}
router_interface_name = {},{}
router_interface_ip_addr = {},{}

host_name = {}
host_gw_name = {}
host_ip_addr = {}
host_gw_addr = {}

link_connect = {}

#functions for autonomous connecting
def create_hostlinks(h_name, my_net):
    h_name = my_net.addHost(name=str(h_name), cls=BaseNode)

def create_routerlinks(r_name, my_net):
    r_name = my_net.addHost(name=str(r_name), cls=Router)  

#funktions for creating autonomous folders         
def create_router_start(r_name):
	for i in range(0, len(r_name)):
		router_start = ["#!/bin/sh\n\n",
			"BASE_DIR=nodeconf\n","NODE_NAME=" + r_name[i] + "\n","FRR_PATH=/usr/lib/frr\n",
			"sysctl -w net.ipv6.conf.all.forwarding=1\n",
			"echo \"no service integrated-vtysh-config\" >> /etc/frr/vtysh.conf\n",
			"chown frr:frrvty $BASE_DIR/$NODE_NAME\n\n",
			"$FRR_PATH/zebra -f $PWD/$BASE_DIR/$NODE_NAME/zebra.conf -d -z $PWD/$BASE_DIR/$NODE_NAME/zebra.sock -i $PWD/$BASE_DIR/$NODE_NAME/zebra.pid\n",
			"sleep 1\n",
			"$FRR_PATH/ospf6d -f $PWD/$BASE_DIR/$NODE_NAME/ospf6d.conf -d -z $PWD/$BASE_DIR/$NODE_NAME/zebra.sock -i $PWD/$BASE_DIR/$NODE_NAME/ospf6d.pid"]

		os.mkdir(r_name[i])
		os.chdir(r_name[i])
		s = open("start.sh", "w+")
		s.writelines(router_start)
		s.close()
		os.chdir('..')

def create_router_ospf6d(r_name, r_i_name, r_id):
	for i in range(0, len(r_name)):
		router_ospf_1 = ["hostname " + r_name[i] + "\n","password zebra\n",
			"log file nodeconf/" + r_name[i] + "/ospf6d.log\n",
			"\ndebug ospf6 message all\n","debug ospf6 lsa unknown\n",
			"debug ospf6 zebra\n","debug ospf6 interface\n","debug ospf6 neighbor\n",
			"debug ospf6 route table\n","debug ospf6 flooding\n","!\n"]
		
		os.chdir(r_name[i])
		o = open("ospf6d.conf", "w+")
		o.writelines(router_ospf_1)

		for j in range(0, len(r_i_name[i])):
			router_ospf_2 = ["interface " + r_i_name[i][j] + "\n",
				" ipv6 ospf6 network broadcast\n","!\n"]
			o.writelines(router_ospf_2)
		
		router_ospf_3 = ["router ospf6\n", " ospf6 router-id " + r_id[i] + "\n",
			" log-adjacency-changes detail\n", " redistribute connected\n"]
		o.writelines(router_ospf_3)

		for j in range(0, len(r_i_name[i])):
			router_ospf_4 = [" interface " + r_i_name[i][j] + " area 0.0.0.0\n"]
			o.writelines(router_ospf_4)

		router_ospf_5 = ["!\n", "interface lo\n", " ipv6 ospf6 network broadcast\n",
			" no link-detect\n", "!\n", "line vty\n", " exec-timeout 0 0\n", "!"]
		o.writelines(router_ospf_5)
		o.close()
		os.chdir('..')

def create_router_zebra(r_name, r_i_name, r_i_ip):
	for i in range(0, len(r_name)):
		router_zebra_1 = ["! -*- zebra -*-\n\n", "!\n", "hostname " + r_name[i] + "\n",
			"log file nodeconf/" + r_name[i] + "/zebra.log\n", "!\n", "debug zebra events\n",
			"debug zebra rib\n", "!\n"]
		
		os.chdir(r_name[i])
		o = open("zebra.conf", "w+")
		o.writelines(router_zebra_1)

		for j in range(0, len(r_i_name[i])):
			router_zebra_2 = ["interface " + r_i_name[i][j] + "\n",
				" ipv6 address " + r_i_ip[i][j] + "\n","!\n"]
			o.writelines(router_zebra_2)

		router_zebra_3 = ["interface lo\n", " ipv6 address fcff:" + str(i+1) + "::1/128\n",
			"!\n", "ipv6 forwarding\n", "!\n", "line vty\n", "!"]
		o.writelines(router_zebra_3)

		o.close()
		os.chdir('..')


def create_host_start(h_name, h_gw_name, h_ip_addr, h_gw_addr):
	for i in range(0, len(h_name)):
		host_start = ["#!/bin/sh\n\n",
			"BASE_DIR=/home/user/mytests/hosts/nodeconf\n",
			"NODE_NAME=" + h_name[i] + "\n",
			"GW_NAME=" + h_gw_name[i] + "\n",
			"IF_NAME=$NODE_NAME-$GW_NAME \n",
			"IP_ADDR=" + h_ip_addr[i] + "\n",
			"GW_ADDR=" + h_gw_addr[i] + "\n",
			"ip -6 addr add $IP_ADDR dev $IF_NAME \n",
			"ip -6 route add default via $GW_ADDR dev $IF_NAME"]

		os.mkdir(h_name[i])
		os.chdir(h_name[i])

		s = open("start.sh", "w+")
		s.writelines(host_start)
		s.close()
		os.chdir('..')

class BaseNode(Host):

    def __init__(self, name, *args, **kwargs):
        dirs = [PRIVDIR]
        Host.__init__(self, name, privateDirs=dirs, *args, **kwargs)
        self.dir = "/tmp/%s" % name
        self.nets = []
        if not os.path.exists(self.dir):
            os.makedirs(self.dir) 

    def config(self, **kwargs):
        # Init steps
        Host.config(self, **kwargs)
        # Iterate over the interfaces
        first = True
        for intf in self.intfs.itervalues():
            # Remove any configured address
            self.cmd('ifconfig %s 0' %intf.name)
            # # For the first one, let's configure the mgmt address
            # if first:
            #   first = False
            #   self.cmd('ip a a %s dev %s' %(kwargs['mgmtip'], intf.name))
        #let's write the hostname in /var/mininet/hostname
        self.cmd("echo '" + self.name + "' > "+PRIVDIR+"/hostname")
        if os.path.isfile(BASEDIR+self.name+"/start.sh") :
            self.cmd('source %s' %BASEDIR+self.name+"/start.sh")
            #print(BASEDIR+self.name)

    def cleanup(self):
        def remove_if_exists (filename):
            if os.path.exists(filename):
                os.remove(filename)

        Host.cleanup(self)
        # Rm dir
        if os.path.exists(self.dir):
            shutil.rmtree(self.dir)

        remove_if_exists(BASEDIR+self.name+"/zebra.pid")
        remove_if_exists(BASEDIR+self.name+"/zebra.log")
        remove_if_exists(BASEDIR+self.name+"/zebra.sock")
        remove_if_exists(BASEDIR+self.name+"/ospf6d.pid")
        remove_if_exists(BASEDIR+self.name+"/ospf6d.log")

        remove_if_exists(OUTPUT_PID_TABLE_FILE)

        # if os.path.exists(BASEDIR+self.name+"/zebra.pid"):
        #     os.remove(BASEDIR+self.name+"/zebra.pid")

        # if os.path.exists(BASEDIR+self.name+"/zebra.log"):
        #     os.remove(BASEDIR+self.name+"/zebra.log")

        # if os.path.exists(BASEDIR+self.name+"/zebra.sock"):
        #     os.remove(BASEDIR+self.name+"/zebra.sock")

        # if os.path.exists(BASEDIR+self.name+"/ospfd.pid"):
        #     os.remove(BASEDIR+self.name+"/ospfd.pid")

        # if os.path.exists(BASEDIR+self.name+"/ospfd.log"):
        #     os.remove(BASEDIR+self.name+"/ospfd.log")

        # if os.path.exists(OUTPUT_PID_TABLE_FILE):
        #     os.remove(OUTPUT_PID_TABLE_FILE)


class Router(BaseNode):
    def __init__(self, name, *args, **kwargs):
        BaseNode.__init__(self, name, *args, **kwargs)

# the add_link function creates a link and assigns the interface names
# as node1-node2 and node2-node1
def add_link (node1, node2):
    Link(node1, node2, intfName1=node1.name+'-'+node2.name,
                       intfName2=node2.name+'-'+node1.name)

def create_topo(my_net):
    for i in range(0, len(host_name)):
        create_hostlinks(host_name[i], my_net)

    for i in range(0, len(router_name)):
        create_routerlinks(router_name[i], my_net)
    
    for i in range(0, len(link_connect)):
        add_link(my_net.getNodeByName(link_connect[i][0]), my_net.getNodeByName(link_connect[i][1]))                                                                  ##########ende

    #note that if the interface names are not provided,
    #the order of adding link will determine the
    #naming of the interfaces (e.g. on r1: r1-eth0, r1-eth1, r1-eth2...)
    # it is possible to provide names as follows
    # Link(h1, r1, intfName1='h1-eth0', intfName2='r1-eth0')
    # the add_link function creates a link and assigns the interface names
    # as node1-node2 and node2-node1

def stopAll():
    # Clean Mininet emulation environment
    os.system('sudo mn -c')
    # Kill all the started daemons
    os.system('sudo killall sshd zebra ospfd')

def extractHostPid (dumpline):
    temp = dumpline[dumpline.find('pid=')+4:]
    return int(temp [:len(temp)-2])


    
def simpleTest():
    "Create and test a simple network"

    #topo = RoutersTopo()
    #net = Mininet(topo=topo, build=False, controller=None)
    net = Mininet(topo=None, build=False, controller=None)
    create_topo(net)

    net.build()
    net.start()


    print "Dumping host connections"
    dumpNodeConnections(net.hosts)
    #print "Testing network connectivity"
    #net.pingAll()

    with open(OUTPUT_PID_TABLE_FILE,"w") as file:
        for host in net.hosts:
            file.write("%s %d\n" % (host, extractHostPid( repr(host) )) )

    CLI( net ) 
    net.stop() 
    stopAll()


with open("input-onlineyamltools.yaml", 'r') as stream:
    network_list = yaml.safe_load(stream)

    for task_obj in enumerate(network_list):
        name = task_obj[1]
        for i in range(0, len(network_list[name])):
            if name == "routers":
                router_name[i] = network_list[name][i]["name"]
                router_id[i] = network_list[name][i]["router-id"]
                for j in range(0, len(network_list[name][i]["interfaces"])):
                    router_interface_name[i][j] = network_list[name][i]["interfaces"][j]["name"]
                    router_interface_ip_addr[i][j] = network_list[name][i]["interfaces"][j]["ip_addr"]

            if name == "hosts":
                host_name[i] = network_list[name][i]["name"]
                host_gw_name[i] = network_list[name][i]["gw_name"]
                host_ip_addr[i] = network_list[name][i]["ip_addr"]
                host_gw_addr[i] = network_list[name][i]["gw_addr"]

            if name == "links":
                link_connect[i] = network_list[name][i] 

if not os.path.exists("nodeconf"):
    os.mkdir("nodeconf")                                            # create nodeconf/
    os.chdir("nodeconf/")                                           # go into nodeconf/
    create_router_start(router_name)
    create_router_ospf6d(router_name,router_interface_name, router_id)
    create_router_zebra(router_name, router_interface_name, router_interface_ip_addr)
    create_host_start(host_name, host_gw_name, host_ip_addr, host_gw_addr)
    

if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    simpleTest()
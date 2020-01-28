#!/usr/bin/env python

import sys
import argparse
import yaml
import os
import shutil

## remove directory nodeconf/
if os.path.exists("nodeconf"):
	shutil.rmtree("nodeconf") 

router_name = {}
router_id = {}
router_interface_name = {},{}
router_interface_ip_addr = {},{}

host_name = {}
host_gw_name = {}
host_ip_addr = {}
host_gw_addr = {}


links = {}

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
			"log file nodeconf/" + r_name[i] + "/zebra.log\n", "!\n", "debug zebtra events\n",
			"debug zebra rib\n", "!\n"]
		
		os.chdir(r_name[i])
		o = open("zebra.conf", "w+")
		o.writelines(router_zebra_1)

		for j in range(0, len(r_i_name[i])):
			router_zebra_2 = ["interface " + r_i_name[i][j] + "\n",
				" ipv6 address " + r_i_ip[i][j] + "\n","!\n"]
			o.writelines(router_zebra_2)

		router_zebra_3 = ["interface lo\n", " ipv6 address fcff:" + str(i+1) + "::1/128\n",
			"!\n", " ipv6 forwarding\n", "!\n", "line vty\n", "!"]
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
				links[i] = network_list[name][i]

	#print(router_interface_name)
	#print(router_interface_ip_addr)
	#print(host_name)
	#print(host_gw_name)
	#print(host_ip_addr)
	#print(host_gw_addr)
	#print(links)

	if not os.path.exists("nodeconf"):
		os.mkdir("nodeconf")											# create nodeconf/
    	os.chdir("nodeconf/")											# go into nodeconf/
    	create_router_start(router_name)
    	create_router_ospf6d(router_name,router_interface_name, router_id)
    	create_router_zebra(router_name, router_interface_name, router_interface_ip_addr)
    	create_host_start(host_name, host_gw_name, host_ip_addr, host_gw_addr)

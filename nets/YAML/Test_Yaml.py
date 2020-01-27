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

def create_router_ospf6d(r_name, i_name, i_ip, h_name):
	for i in range(0, len(r_name)):
		router_ospf_1 = ["hostname " + r_name[i] + "\n","password zebra\n",
			"log file nodeconf/" + r_name[i] + "/ospf6d.log\n",
			"\ndebug ospf6 message all\n","debug ospf6 lsa unknown\n",
			"debug ospf6 zebra\n","debug ospf6 interface\n","debug ospf6 neighbor\n",
			"debug ospf6 route table\n","debug ospf6 flooding\n","!\n"]
		
		#router_ospf_2 = ["interface" + r_name[i] + "-" + h_name[i] + "\n",
		#	"ipv6 ospf6 network broadcast\n","!\n"]

		os.chdir(r_name[i])
		o = open("ospf6d.conf", "w+")
		o.writelines(router_ospf_1)
		o.close()
		os.chdir('..')

def create_router_zebra(r_name, r_id, i_name, i_ip):
	for i in range(0, len(r_name)):
		os.chdir(r_name[i])
		o = open("zebra.conf", "w+")
		o.close()
		os.chdir('..')


with open("input-onlineyamltools.yaml", 'r') as stream:
	network_list = yaml.safe_load(stream)

	for task_obj in enumerate(network_list):
		name = task_obj[1]
		#print("task name:" + name)
		for i in range(0, len(task_obj)):
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


	print(host_name)
	print(host_gw_name)
	print(host_ip_addr)
	print(host_gw_addr)

	if not os.path.exists("nodeconf"):
		os.mkdir("nodeconf")											# create nodeconf/
    	os.chdir("nodeconf/")											# go into nodeconf/
    	create_router_start(router_name)
    	create_router_ospf6d(router_name, router_id, router_interface_name, router_interface_ip_addr)
    	create_router_zebra(router_name, router_interface_name, router_interface_ip_addr, host_name)

#!/bin/bash

BASE_DIR=/home/user/Progetto/1920-srv6-tutorial/nets/8routers-isis-ipv6/nodeconf
NODE_NAME=h13
GW_NAME=r1
IF_NAME=$NODE_NAME-$GW_NAME
IP_ADDR=fd00:0:13::2/64
GW_ADDR=fd00:0:13::1

ip -6 addr add $IP_ADDR dev $IF_NAME 
ip -6 route add default via $GW_ADDR dev $IF_NAME

SW_NAME=sw
MGMT_IF_NAME=$NODE_NAME-$SW_NAME
MGMT_IP_ADDR=fcfd:0:0:1:3::1/48
ip -6 addr add $MGMT_IP_ADDR dev $MGMT_IF_NAME

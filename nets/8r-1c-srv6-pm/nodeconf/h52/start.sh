#!/bin/bash

BASE_DIR=/home/user/Progetto/1920-srv6-tutorial/nets/8routers-isis-ipv6/nodeconf
NODE_NAME=h52
GW_NAME=r5
IF_NAME=$NODE_NAME-$GW_NAME
IP_ADDR=fd00:0:52::2/64
GW_ADDR=fd00:0:52::1

ip -6 addr add $IP_ADDR dev $IF_NAME 
ip -6 route add default via $GW_ADDR dev $IF_NAME

SW_NAME=sw
MGMT_IF_NAME=$NODE_NAME-$SW_NAME
MGMT_IP_ADDR=fcfd:0:0:5:2::1/48
ip -6 addr add $MGMT_IP_ADDR dev $MGMT_IF_NAME

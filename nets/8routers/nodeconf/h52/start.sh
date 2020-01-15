#!/bin/sh

BASE_DIR=/home/user/mytests/ospf3routers/nodeconf
NODE_NAME=h52
GW_NAME=r5
IF_NAME=$NODE_NAME-$GW_NAME
IP_ADDR=fd00:0:52::2/64
GW_ADDR=fd00:0:52::1

ip -6 addr add $IP_ADDR dev $IF_NAME 
ip -6 route add default via $GW_ADDR dev $IF_NAME
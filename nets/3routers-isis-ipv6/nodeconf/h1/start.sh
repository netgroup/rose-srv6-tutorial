#!/bin/sh

BASE_DIR=/home/user/Progetto/1920-srv6-tutorial/nets/3routers-isis-ipv6/nodeconf
NODE_NAME=h1
GW_NAME=r1
IF_NAME=$NODE_NAME-$GW_NAME
IP_ADDR=fd00:0:11::2/64
GW_ADDR=fd00:0:11::1

ip addr add $IP_ADDR dev $IF_NAME 
ip route add default via $GW_ADDR dev $IF_NAME

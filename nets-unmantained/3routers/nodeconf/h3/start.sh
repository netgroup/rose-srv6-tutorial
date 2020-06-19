#!/bin/sh

NODE_NAME=h3
GW_NAME=r3
IF_NAME=$NODE_NAME-$GW_NAME
IP_ADDR=10.103.0.2/16
GW_ADDR=10.103.0.1

ip addr add $IP_ADDR dev $IF_NAME 
ip route add default via $GW_ADDR dev $IF_NAME


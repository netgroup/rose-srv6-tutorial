#!/bin/sh

NODE_NAME=h2
GW_NAME=r2
IF_NAME=$NODE_NAME-$GW_NAME
IP_ADDR=10.102.0.2/16
GW_ADDR=10.102.0.1

ip addr add $IP_ADDR dev $IF_NAME 
ip route add default via $GW_ADDR dev $IF_NAME

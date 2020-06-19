#!/bin/sh

NODE_NAME=controller
GW_NAME=r2
IF_NAME=$NODE_NAME-$GW_NAME
IP_ADDR=fcff:2:c::2/48
GW_ADDR=fcff:2:c::1

ip -6 addr add $IP_ADDR dev $IF_NAME 
ip -6 route add fc00::/8 via $GW_ADDR dev $IF_NAME
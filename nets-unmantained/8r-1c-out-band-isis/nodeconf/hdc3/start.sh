#!/bin/sh

NODE_NAME=hdc3
GW_NAME=r5
IF_NAME=$NODE_NAME-$GW_NAME
IP_ADDR=fcff:5:1::2/48
GW_ADDR=fcff:5:1::1

ip -6 addr add $IP_ADDR dev $IF_NAME 
ip -6 route add default via $GW_ADDR dev $IF_NAME
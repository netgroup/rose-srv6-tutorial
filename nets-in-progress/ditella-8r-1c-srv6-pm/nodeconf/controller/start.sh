#!/bin/sh

NODE_NAME=controller
SW_NAME=sw
IF_NAME=$NODE_NAME-$SW_NAME
IP_ADDR=fcfd:0:0:fd::1/48

ip -6 addr add $IP_ADDR dev $IF_NAME
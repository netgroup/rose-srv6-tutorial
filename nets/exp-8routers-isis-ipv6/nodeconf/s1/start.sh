#!/bin/sh

BASE_DIR=nodeconf
NODE_NAME=s1

#enable creating bridge
ip link add br0 type bridge
ip link set br0 up

# add all interfaces to bridge br0
for dev in $(ip -o -6 a | awk '{ print $2 }' | grep -v "lo")
do
ip link set $dev master br0
done

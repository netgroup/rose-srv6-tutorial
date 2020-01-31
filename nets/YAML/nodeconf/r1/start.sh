#!/bin/sh

BASE_DIR=nodeconf
NODE_NAME=r1
FRR_PATH=/usr/lib/frr
sysctl -w net.ipv6.conf.all.forwarding=1
echo "no service integrated-vtysh-config" >> /etc/frr/vtysh.conf
chown frr:frrvty $BASE_DIR/$NODE_NAME

$FRR_PATH/zebra -f $PWD/$BASE_DIR/$NODE_NAME/zebra.conf -d -z $PWD/$BASE_DIR/$NODE_NAME/zebra.sock -i $PWD/$BASE_DIR/$NODE_NAME/zebra.pid
sleep 1
$FRR_PATH/ospf6d -f $PWD/$BASE_DIR/$NODE_NAME/ospf6d.conf -d -z $PWD/$BASE_DIR/$NODE_NAME/zebra.sock -i $PWD/$BASE_DIR/$NODE_NAME/ospf6d.pid
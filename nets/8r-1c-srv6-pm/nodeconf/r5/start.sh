#!/bin/bash

readonly BASE_DIR="nodeconf"
readonly COMMON_DIR="common"
readonly NODE_NAME="r5"
readonly FRR_PATH="/usr/lib/frr"

# Punt interfce name
readonly PUNT_IFNAME="punt0"

# Node working directory
readonly WDIR="${PWD}/${BASE_DIR}/${NODE_NAME}"
# Common working directory
readonly CDIR="${PWD}/${BASE_DIR}/${COMMON_DIR}"

# script for setting up the env for pfplm using iptables/ipset
readonly IPSET_START="${CDIR}/ipset_start.sh"

# script for setting up the env for pfplm using ebpf programs
# readonly EBPF_START="${WDIR}/ebpf_start.sh"

# This file contains the configuration of the node that should be enforced by
# the controller.
#
# IF you need to add/remove/change flows (and all the configs that SHOULD BE
# enforced by the controller on this NODE):
#	!!! PLEASE EDIT THIS FILE !!!
readonly CONTROLLER_CFG="${WDIR}/controller.cfg"

# daemon file configs
# These variable can be rewritten by the EBPFs scripts:
#	DO NOT MAKE THEM READ ONLY!
ZEBRA_CFG="${WDIR}/zebra.conf"
ISIS_CFG="${WDIR}/isisd.conf"


############################
### BEWARE TO EDIT BELOW ###
############################

source "${CDIR}/commons.sh" || exit $?

#enable IPv6 forwarding
#sysctl -w net.ipv4.ip_forward=1
sysctl -w net.ipv6.conf.all.forwarding=1
#disable reverse path filtering (needed for dynamic routing)
#sysctl -w net.ipv4.conf.all.rp_filter=0
#sysctl -w net.ipv4.conf.default.rp_filter=0
#the following for loop also disables all and default
#for i in /proc/sys/net/ipv4/conf/*/rp_filter ; do
  #echo 0 > $i
#done

mount -t bpf bpf /sys/fs/bpf/

# source_file_if_defined "${EBPF_START}"
source_file_if_defined "${IPSET_START}"

echo "no service integrated-vtysh-config" >> /etc/frr/vtysh.conf
chown frr:frrvty "${BASE_DIR}/${NODE_NAME}"
#chown quagga:quagga "${BASE_DIR}/${NODE_NAME}"

${FRR_PATH}/zebra -f ${ZEBRA_CFG} -d -z ${WDIR}/zebra.sock -i ${WDIR}/zebra.pid

sleep 1

${FRR_PATH}/isisd -f ${ISIS_CFG} -d -z ${WDIR}/zebra.sock -i ${WDIR}/isisd.pid

# enable Segment Routing for IPv6
sysctl -w net.ipv6.conf.all.seg6_enabled=1
for dev in $(ip -o -6 a | awk '{ print $2 }' | grep -v "lo")
do
   sysctl -w net.ipv6.conf.$dev.seg6_enabled=1
done

# Add punt0 interface
ip link add ${PUNT_IFNAME} type dummy
ip link set ${PUNT_IFNAME} up

source_file_if_defined "${CONTROLLER_CFG}"

#!/bin/bash

### !!! DO NOT CALL THIS FILE DIRECTLY !!! ###
if [ -z "${EBPF_START+x}" ]; then
	echo "EBPF_START is unset. Do not call this script directly"
	exit 1
fi

export EBPF_HELPER="$CDIR/ebpf_helper.sh"

source "${EBPF_HELPER}"
[ ! -f "${EBPF_CLI}" ] && exit $?


# Prepare the networking for supporting the "egress" path for the ebpf pfplm
# program.
prepare_netdev r8-r6
move_ip_addr r8-r6

ZEBRA_CFG="$(prepare_daemon_conf "$WDIR/zebra.conf" r8-r6)" \
	|| { echo "Error during the creation of ebpf zebra .conf"; exit 1; }

ISIS_CFG="$(prepare_daemon_conf "$WDIR/isisd.conf" r8-r6)" \
	|| { echo "Error during the creation of ebpf isisd .conf"; exit 1; }

# mount the bpf filesystem.
# Note: childs of the launching (parent) bash can access this instance
# of the bpf filesystem. If you need to get access to the bpf filesystem
# (where maps are available), you need to use nsenter with -m and -t
# that points to the pid of the parent process (launching bash).
mount -t bpf bpf /sys/fs/bpf/ || exit $?


# Load the ebpf pfplm program on the r8-r6 egress path
# Set the color=2 on the egress path of r8-r6
xdp_pfplm_load r8-r6 egr
xdp_pfplm_set_color r8-r6 2

# Load the ebpf pfplm program on the r8-r6 ingress path
# NOTE: we do not need to set the color on the ingress path
xdp_pfplm_load r8-r6 igr

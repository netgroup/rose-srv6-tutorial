#!/bin/bash

# Error codes
# @see /usr/include/sysexits.h

readonly EX_OK=0		# /* successful termination */
readonly EX__BASE=64		# /* base value for error messages */
readonly EX_USAGE=64		# /* command line usage error */
readonly EX_DATAERR=65		# /* data format error */
readonly EX_NOINPUT=66		# /* cannot open input */
readonly EX_NOUSER=67		# /* addressee unknown */
readonly EX_NOHOST=68		# /* host name unknown */
readonly EX_UNAVAILABLE=69	# /* service unavailable */
readonly EX_SOFTWARE=70		# /* internal software error */
readonly EX_OSERR=71		# /* system error (e.g., can't fork) */
readonly EX_OSFILE=72		# /* critical OS file missing */
readonly EX_CANTCREAT=73	# /* can't create (user) output file */
readonly EX_IOERR=74		# /* input/output error */
readonly EX_TEMPFAIL=75		# /* temp failure; user is invited to retry */
readonly EX_PROTOCOL=76		# /* remote error in protocol */
readonly EX_NOPERM=77		# /* permission denied */
readonly EX_CONFIG=78		# /* configuration error */

if [ -n "${CDIR+x}" ]; then
	readonly export EBPF_CLI="${CDIR}/ebpf_py_cli.py"
else
	# Stand-alone
	__HELPER_DIR="$(dirname -- $(readlink -f -- "${BASH_SOURCE}"))"
	readonly export EBPF_CLI="${__HELPER_DIR}/ebpf_py_cli.py"
fi

[ ! -f "${EBPF_CLI}" ] && exit 1

# retrieves the ip addresses set on a given interface
# NOTE: do not move ipv6 link-local addresses
function get_ip_addr()
{
	local ifname="$1"
	local addrs

	addrs="$(ip -o addr show "${ifname}" | awk '{ print $4 }')" \
		|| return $?
	echo "${addrs}"

	return 0
}

function dev_exists()
{
	local ifname="$1"

	if [ -z "${ifname}" ]; then
		return ${EX_DATAERR}
	fi

	ip link show "${ifname}" > /dev/null 2>&1
	return $?
}

# moves the ip addresses from src_dev to dst_dev
function move_ip_addr()
{
	local dst_dev="$1"
	local src_dev="$2"
	local addrs
	local res
	local i

	addrs="$(get_ip_addr "${src_dev}")" || return $?

	res=0
	for i in ${addrs}; do
		# we skip ipv6 link-local addresses
		echo "${i}" | grep -q -E '^fe80::' && continue;

		ip addr add "${i}" dev "${dst_dev}" || { res=$?; break; }
	done

	if [ ${res} -ne 0 ]; then
		ip addr flush dev "${dst_dev}" || return $?
		return ${EX_IOERR}
	fi

	for i in ${addrs}; do
		# we skip ipv6 link-local addresses
		echo "${i}" | grep -q -E '^fe80::' && continue

		ip addr del "${i}" dev "${src_dev}"
	done

	return 0
}

function clean_netdev()
{
	local ifname="$1"
	local ifname_igr
	local ifname_egr
	local ifname_br

	dev_exists "${ifname}" || return $?

	ifname_igr="${ifname}_igr"
	ifname_egr="${ifname}_egr"
	ifname_br="${ifname}_br"

	dev_exists "${ifname_igr}" && move_ip_addr "${ifname}" "${ifname_igr}"

	ip link del "${ifname_igr}" > /dev/null 2>&1
	# we do not need to delete _egr because it's a side of a veth pair
	ip link del "${ifname_br}" > /dev/null 2>&1

	return 0
}

function prepare_netdev()
{
	local ifname="$1"
	local ifname_igr
	local ifname_egr
	local ifname_br
	local res=0

	dev_exists "${ifname}" || return $?

	# clean the node if needed
	clean_netdev "${ifname}"

	ifname_igr="${ifname}_igr"
	ifname_egr="${ifname}_egr"
	ifname_br="${ifname}_br"

	ip link add dev "${ifname_igr}" type veth peer name "${ifname_egr}" \
		|| return $?

	# we create the bridge for interconnecting the ifname_egr with the
	# ifname.
	#
	# NOTE: goto does not exist... so we need to get something similar with
	# if (true) {  if(..) break; }
	if [ 1 ]; then
		ip link add name "${ifname_br}" type bridge \
			|| { res=$?; break; }
		ip link set dev "${ifname_egr}" master "${ifname_br}" \
			|| { res=$?; break; }
		ip link set dev "${ifname}" master "${ifname_br}" \
			|| { res=$?; break; }

		ip link set dev "${ifname_br}" up || { res=$?; break; }
		ip link set dev "${ifname_igr}" up || { res=$?; break; }
		ip link set dev "${ifname_egr}" up || { res=$?; break; }
	fi

	if [ $res -ne 0 ]; then
		#clean up
		clean_node "${ifname}"
	fi

	move_ip_addr "${ifname_igr}" "${ifname}" \
		|| { res=$?; clean_netdev "${ifname}"; return ${res}; }

	return 0
}

# prepares a compatible zebra.conf (ebpf_zebra.conf) file for working with
# the ebpf pfplm programs. The function takes two parameters:
#  1) the fullpath zebra conf file
#  2) the interface where the ebpf program will be attached on the egress
#     direction.
function prepare_daemon_conf()
{
	local ifname="$2"
	local ifname_igr
	local cfg_ebpf
	local cfg="$1"
	local res

	cfg="$(realpath "${cfg}")" || return $?
	if [ ! -f "${cfg}" ]; then
		return ${EX_NOINPUT}
	fi

	dev_exists "${ifname}" || return $?
	ifname_igr="${ifname}_igr"

	# i.e: filename from zebra.conf to ebpf_zebra.conf with the full path
	cfg_ebpf="$(dirname "${cfg}")/ebpf_$(basename "${cfg}")"

	cat "${cfg}" | sed "s/${ifname}/${ifname_igr}/g" > "${cfg_ebpf}" \
		|| { res=$?; rm "${cfg_ebpf}"; return $?; }

	echo "${cfg_ebpf}"

	return 0
}

function clean_daemon_conf()
{
	local cfg_ebpf
	local cfg="$1"

	cfg="$(realpath "${cfg}")" || return $?
	if [ ! -f "${cfg}" ]; then
		return ${EX_NOINPUT}
	fi

	# i.e: filename from zebra.conf to ebpf_zebra.conf with the full path
	cfg_ebpf="$(dirname "${cfg}")/ebpf_$(basename "${cfg}")"
	if [ -f "${cfg_ebpf}" ]; then
		# we remove the file
		rm "${cfg_ebpf}" || return $?
	fi

	return 0
}

function xdp_pfplm_load()
{
	local direction="$2"
	local ifname="$1"
	local ifname_dir

	ifname_dir="${ifname}_${direction}"

	"${EBPF_CLI}" load "${ifname_dir}" "${direction}" || return $?

	return 0
}

function xdp_pfplm_unload()
{
	local direction="$2"
	local ifname="$1"
	local ifname_dir

	ifname_dir="${ifname}_${direction}"

	"${EBPF_CLI}" unload "${ifname_dir}" || return $?

	return 0
}

function xdp_pfplm_set_color()
{
	local ifname="$1"
	local ifname_egr
	local color="$2"

	# change color makes sense only for the egress path
	ifname_egr="${ifname}_egr"

	"${EBPF_CLI}" set_color "${ifname_egr}" "${color}" || return $?

	return 0
}

function xdp_pfplm_get_color()
{
	local ifname="$1"
	local ifname_egr
	local color

	# change color makes sense only for the egress path
	ifname_egr="${ifname}_egr"

	color="$("${EBPF_CLI}" get_color "${ifname_egr}")" || return $?
	echo "${color}"

	return 0
}

function xdp_pfplm_add_flow()
{
	local direction"=$2"
	local ifname="$1"
	local ifname_dir
	local segs="$3"

	ifname_dir="${ifname}_${direction}"

	"${EBPF_CLI}" add_flow "${ifname_dir}" "${segs}" || return $?

	return 0
}

function xdp_pfplm_del_flow()
{
	local direction"=$2"
	local ifname="$1"
	local ifname_dir
	local segs="$3"

	ifname_dir="${ifname}_${direction}"

	"${EBPF_CLI}" del_flow "${ifname_dir}" "${segs}" || return $?

	return 0
}

function xdp_pfplm_get_flow_stats()
{
	local direction"=$2"
	local ifname="$1"
	local ifname_dir
	local color="$4"
	local segs="$3"
	local pkts

	ifname_dir="${ifname}_${direction}"

	pkts="$("${EBPF_CLI}" get_flow_stats \
		"${ifname_dir}" "${segs}" "${color}")" || return $?
	echo "${pkts}"

	return 0
}

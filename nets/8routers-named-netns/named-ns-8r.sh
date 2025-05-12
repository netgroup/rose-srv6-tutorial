#!/bin/bash

set -eu

readonly TMUX="hawaii"
# Kill tmux previous session
tmux kill-session -t "${TMUX}" 2>/dev/null || true

readonly ROUTERS="r1 r2 r3 r4 r5 r6 r7 r8"
readonly HOSTS="h11 h12 h13 h31 h32 h33 h51 h52 h53 h81 h82 h83"
readonly ALL_NODES="${ROUTERS} ${HOSTS}"

declare -a LINK_PAIRS=(
# XXX: order matters! please put always a node rX before a node rY where X < Y
# XXX: suppored up to 9 hosts (i.e., h[0-9][0-9]) and 9 routers (i.e., r[0-9]).
	"h11,r1"
	"h12,r1"
	"h13,r1"
	"h31,r3"
	"h32,r3"
	"h33,r3"
	"h51,r5"
	"h52,r5"
	"h53,r5"
	"h81,r8"
	"h82,r8"
	"h83,r8"
	"r1,r2"
	"r2,r3"
	"r2,r7"
	"r3,r4"
	"r4,r5"
	"r4,r6"
	"r5,r6"
	"r6,r7"
	"r6,r8"
	"r7,r8"
); readonly LINK_PAIRS

declare -a ROUTES=(
# r1 routes
	"r1>r3,r2"
	"r1>r4,r2"
	"r1>r5,r2"
	"r1>r6,r2"
	"r1>r7,r2"
	"r1>r8,r2"
# r2 routes
	"r2>r4,r3"
	"r2>r5,r3"
	"r2>r6,r3"
	"r2>r8,r3"
# r3 routes
	"r3>r1,r2"
	"r3>r5,r4"
	"r3>r6,r4"
	"r3>r7,r4"
	"r3>r8,r4"
# r4 routes
	"r4>r1,r3"
	"r4>r2,r3"
	"r4>r7,r6"
	"r4>r8,r6"
# r5 routes
	"r5>r1,r4"
	"r5>r2,r4"
	"r5>r3,r4"
	"r5>r7,r6"
	"r5>r8,r6"
# r6 routes
	"r6>r1,r4"
	"r6>r2,r4"
	"r6>r3,r4"
# r7 routes
	"r7>r1,r6"
	"r7>r3,r6"
	"r7>r4,r6"
	"r7>r5,r6"
# r8 routes
	"r8>r1,r6"
	"r8>r2,r6"
	"r8>r3,r6"
	"r8>r4,r6"
	"r8>r5,r6"
); readonly ROUTES

# SRv6 policies
declare -a SRV6_POLICIES=(
	# rt src, hs dst, mode, end nodes, decap node
	"r1,h81,srh,r3 r5,r8"
	"r8,h11,srh,,r1"
	"r1,h82,red,r5 r7,r8"
	"r8,h12,red,,r1"
	"r1,h83,red,r2 r7 r4 r5,r8"
	"r8,h13,srh,r7 r6 r5 r3 r2,r1"
); readonly SRV6_POLICIES

declare -a TMUX_WIN=(
	"h11"
	"h12"
	"r1"
	"r2"
	"r3"
	"r2"
	"r5"
	"r6"
	"r7"
	"r8"
	"h81"
	"h82"
); readonly TMUX_WIN

readonly UNDERLAY_RT_PREFIX="fcf0:0"
readonly UNDERLAY_RT_PREFIX_LEN=64
readonly UNDERLAY_HS_PREFIX="fd00:0"
readonly UNDERLAY_HS_PREFIX_LEN=64

# Loopback address prefix is used for SID reachability
readonly RT_LO_PREFIX="fcff"
readonly RT_LO_PREFIX_LEN=32

readonly END_FUNC="0e"
readonly DT6_LEGACY_FUNC="d6"
readonly SID_END_FMT="${RT_LO_PREFIX}:%d::${END_FUNC}"
readonly SID_DT6_LEGACY_FMT="${RT_LO_PREFIX}:%d::${DT6_LEGACY_FUNC}"
readonly DT6_LEGACY_TABLE="main"

readonly CSID_GLOBAL_LOC="${RT_LO_PREFIX}"
readonly CSID_FUNC_FMT="0%d%s"
readonly CSID_LOCATOR_FUNC_FMT="${CSID_GLOBAL_LOC}:${CSID_FUNC_FMT}"
readonly CSID_LOCATOR_PREFIX=24

readonly CSID_GLOB_LOCATOR_LEN=16
readonly CSID_FUNC_LEN=16
readonly CSID_LOC_FUNC_LEN="$((CSID_GLOB_LOCATOR_LEN + CSID_FUNC_LEN))"

readonly DUM_IFNAME="dum0"

cleanup()
{
	local node

	for node in ${ALL_NODES}; do
		ip netns del "${node}" 2>/dev/null || true
	done
}

create_netns()
{
	local nsname="${1}"

	ip netns add "${nsname}"

	ip netns exec "${nsname}" sysctl -wq net.ipv6.conf.all.accept_dad=0
	ip netns exec "${nsname}" sysctl -wq net.ipv6.conf.default.accept_dad=0
	ip netns exec "${nsname}" sysctl -wq net.ipv6.conf.all.forwarding=1

	ip netns exec "${nsname}" sysctl -wq net.ipv4.ip_forward=1

	ip netns exec "${nsname}" sysctl -wq net.ipv4.conf.all.rp_filter=0
	ip netns exec "${nsname}" sysctl -wq net.ipv4.conf.default.rp_filter=0

	ip -netns "${nsname}" link set dev lo up
}

check_node_name()
{
	local node="${1}"

	if [[ "${node}" =~ ^h[0-9][0-9]$ ]]; then
		return 0
	elif [[ "${node}" =~ ^r[0-9]$ ]]; then
		return 0
	fi

	echo "Node name ${node} is not valid"
	exit 1
}

create_node()
{
	local node="${1}"

	check_node_name "${node}"
	create_netns "${node}"
}

get_id_node()
{
	local node="${1}"

	# remove the first char from the name indicating the type of the node,
	# i.e., r for router, h for host.
	echo "${node#?}"
}

config_rt_loopback_address()
{
	local rtnode="${1}"
	local id="$(get_id_node "${rtnode}")"

	ip -netns "${rtnode}" addr add \
		"${RT_LO_PREFIX}:${id}::1/${RT_LO_PREFIX_LEN}" dev lo
}

create_routers()
{
	local rt

	# create routers
	for rt in ${ROUTERS}; do
		create_node "${rt}"
		config_rt_loopback_address "${rt}"

		# add dummy interfaces for srv6
		ip -netns "${rt}" link add "${DUM_IFNAME}" type dummy
		ip -netns "${rt}" link set dev "${DUM_IFNAME}" up
	done
}

create_hosts()
{
	local ht

	# create hosts
	for ht in ${HOSTS}; do
		create_node "${ht}"
	done
}

get_ifname()
{
	local src_node="${1}"
	local dst_node="${2}"

	echo "${src_node}-${dst_node}"
}

setup_rt_rt_addresses_link()
{
	local src_node="${1}"
	local src_ifname="${2}"
	local dst_node="${3}"
	local dst_ifname="${4}"
	local src_id="$(get_id_node "${src_node}")"
	local dst_id="$(get_id_node "${dst_node}")"

	ip -netns "${src_node}" addr add \
		"${UNDERLAY_RT_PREFIX}:${src_id}:${dst_id}::${src_id}/${UNDERLAY_RT_PREFIX_LEN}" \
		dev "${src_ifname}"

	ip -netns "${dst_node}" addr add \
		"${UNDERLAY_RT_PREFIX}:${src_id}:${dst_id}::${dst_id}/${UNDERLAY_RT_PREFIX_LEN}" \
		dev "${dst_ifname}"
}

setup_hs_rt_addresses_link()
{
	local src_node="${1}"
	local src_ifname="${2}"
	local dst_node="${3}"
	local dst_ifname="${4}"
	local src_id="$(get_id_node "${src_node}")"
	local dst_id="$(get_id_node "${dst_node}")"

	ip -netns "${src_node}" addr add \
		"${UNDERLAY_HS_PREFIX}:${src_id}::2/${UNDERLAY_HS_PREFIX_LEN}" \
		dev "${src_ifname}"

	ip -netns "${dst_node}" addr add \
		"${UNDERLAY_HS_PREFIX}:${src_id}::1/${UNDERLAY_HS_PREFIX_LEN}" \
		dev "${dst_ifname}"

	# add default route for the hostnode (always the @src_node)
	ip -netns "${src_node}" route add default \
		via "${UNDERLAY_HS_PREFIX}:${src_id}::1" \
		dev "${src_ifname}"
}

create_veth_links()
{
	local src_node="${1}"
	local dst_node="${2}"
	local src_ifname
	local dst_ifname

	src_ifname="$(get_ifname "${src_node}" "${dst_node}")"
	dst_ifname="$(get_ifname "${dst_node}" "${src_node}")"

	ip link \
		add "${src_ifname}" \
		netns "${src_node}" \
		type veth \
		peer name "${dst_ifname}" \
		netns "${dst_node}"

	ip -netns "${src_node}" link set dev "${src_ifname}" up
	ip -netns "${dst_node}" link set dev "${dst_ifname}" up
}

setup_address_links()
{
	local src_node="${1}"
	local dst_node="${2}"
	local src_ifname
	local dst_ifname

	src_ifname="$(get_ifname "${src_node}" "${dst_node}")"
	dst_ifname="$(get_ifname "${dst_node}" "${src_node}")"

	if [[ "${src_node}" == r* ]]; then
		setup_rt_rt_addresses_link \
			"${src_node}" "${src_ifname}" \
			"${dst_node}" "${dst_ifname}"
	elif [[ "${src_node}" == h* ]]; then
		setup_hs_rt_addresses_link \
			"${src_node}" "${src_ifname}" \
			"${dst_node}" "${dst_ifname}"
	else
		echo "Invalid node name ${src_node}"
		exit 1
	fi
}

setup_rt_neigh_reachability()
{
	local src_node="${1}"
	local dst_node="${2}"
	local csid_loc_func
	local src_id
	local dst_id

	src_id="$(get_id_node "${src_node}")"
	dst_id="$(get_id_node "${dst_node}")"

	# For plain SID
	ip -netns "${src_node}" route add \
		"${RT_LO_PREFIX}:${dst_id}::/${RT_LO_PREFIX_LEN}" \
		via "${UNDERLAY_RT_PREFIX}:${src_id}:${dst_id}::${dst_id}"

	ip -netns "${dst_node}" route add \
		"${RT_LO_PREFIX}:${src_id}::/${RT_LO_PREFIX_LEN}" \
		via "${UNDERLAY_RT_PREFIX}:${src_id}:${dst_id}::${src_id}"

	# For C-SID
	csid_loc_func="$(printf "${CSID_LOCATOR_FUNC_FMT}" "${dst_id}" "00")"
	ip -netns "${src_node}" route add \
		"${csid_loc_func}::/${CSID_LOCATOR_PREFIX}" \
		via "${UNDERLAY_RT_PREFIX}:${src_id}:${dst_id}::${dst_id}"

	csid_loc_func="$(printf "${CSID_LOCATOR_FUNC_FMT}" "${src_id}" "00")"
	ip -netns "${dst_node}" route add \
		"${csid_loc_func}::/${CSID_LOCATOR_PREFIX}" \
		via "${UNDERLAY_RT_PREFIX}:${src_id}:${dst_id}::${src_id}"
}

setup_all_rts_neigh_reachability()
{
	# save the original IFS
	local OLDIFS="${IFS}"
	local src_node
	local dst_node
	local link

	for link in "${LINK_PAIRS[@]}"; do
		IFS=',' read -r src_node dst_node <<< "${link}"

		if [[ "${src_node}" == r* ]]; then
			setup_rt_neigh_reachability "${src_node}" "${dst_node}"
		fi
	done

	# restore the IFS
	IFS="${OLDIFS}"
}

get_network_prefix()
{
	local rt="${1}"
	local neigh="${2}"
	local p="${rt}"
	local q="${neigh}"

	if [ "${p}" -gt "${q}" ]; then
		p="${q}"; q="${rt}"
	fi

	echo "${UNDERLAY_RT_PREFIX}:${p}:${q}"
}

setup_rt_routes()
{
	local src_node="${1}"
	local dst_node="${2}"
	local neigh_node="${3}"
	local csid_loc_func
	local prefix_net
	local neigh_id
	local src_id
	local dst_id

	src_id="$(get_id_node "${src_node}")"
	dst_id="$(get_id_node "${dst_node}")"
	neigh_id="$(get_id_node "${neigh_node}")"

	prefix_net="$(get_network_prefix "${src_id}" "${neigh_id}")"

	# XXX: route src is necessary as a router doesn't know how to reach
	# networks that are not directly connected. loopback addresses and
	# subnets are always reachable.
	ip -netns "${src_node}" route add \
		"${RT_LO_PREFIX}:${dst_id}::/${RT_LO_PREFIX_LEN}" \
		via "${prefix_net}::${neigh_id}" \
		src "${RT_LO_PREFIX}:${src_id}::1"

	# C-SID
	csid_loc_func="$(printf "${CSID_LOCATOR_FUNC_FMT}" "${dst_id}" "00")"
	ip -netns "${src_node}" route add \
		"${csid_loc_func}::/${CSID_LOCATOR_PREFIX}" \
		via "${prefix_net}::${neigh_id}" \
		src "${RT_LO_PREFIX}:${src_id}::1"
}

setup_all_rt_routes()
{
	local neigh_node
	local src_node
	local dst_node
	local route
	local tmp

	# WARNING black magic below... :-)
	for route in "${ROUTES[@]}"; do
		# remove everything from the frist '>' onward, leaving the
		# src_node
		src_node="${route%%>*}"

		# remove everything up to and incluing '>', leaving the
		# dst_node and the neigh_node
		tmp="${route#*>}"

		# remove everything from the ',' onward leaving the dst_node
		dst_node="${tmp%%,*}"

		# remove everything up to and including the first ',' leaving
		# the neigh_node
		neigh_node="${tmp#*,}"

		setup_rt_routes "${src_node}" "${dst_node}" "${neigh_node}"
	done
}

setup_rt_sids()
{
	local node="${1}"
	local csid_loc_func
	local node_id
	local end_sid
	local dt6_sid

	node_id="$(get_id_node "${node}")"
	end_sid="$(printf "${SID_END_FMT}" "${node_id}")"
	dt6_sid="$(printf "${SID_DT6_LEGACY_FMT}" "${node_id}")"

	# SRv6 End behavior
	ip -netns "${node}" route add \
		"${end_sid}" encap seg6local \
		action End \
		count \
		dev "${DUM_IFNAME}"

	# SRv6 End.DT6 legacy behavior
	ip -netns "${node}" route add \
		"${dt6_sid}" encap seg6local \
		action End.DT6 table ${DT6_LEGACY_TABLE} \
		count \
		dev "${DUM_IFNAME}"

	# C-SID

	# SRv6 End with next-csid
	csid_loc_func="$(printf "${CSID_LOCATOR_FUNC_FMT}" \
				 "${node_id}" "${END_FUNC}")"
	ip -netns "${node}" route add \
		"${csid_loc_func}::/${CSID_LOC_FUNC_LEN}" encap seg6local \
		action End flavors next-csid \
		lblen "${CSID_GLOB_LOCATOR_LEN}" \
		nflen "${CSID_FUNC_LEN}" \
		count \
		dev "${DUM_IFNAME}"

	# SRv6 End.DT6 legacy with C-SID
	csid_loc_func="$(printf "${CSID_LOCATOR_FUNC_FMT}" \
				 "${node_id}" "${DT6_LEGACY_FUNC}")"
	ip -netns "${node}" route add \
		"${csid_loc_func}::/${CSID_LOC_FUNC_LEN}" encap seg6local \
		action End.DT6 table ${DT6_LEGACY_TABLE} \
		count \
		dev "${DUM_IFNAME}"
}

setup_all_rts_sids()
{
	local rt

	for rt in ${ROUTERS[@]}; do
		setup_rt_sids "${rt}"
	done
}

setup_srv6_policy()
{
	local src_node="${1}"
	local dst_node="${2}"
	local enc_type="${3}"
	local end_nodes="${4}"
	local decap_node="${5}"
	local sidlist=''
	local carrier=''
	local node_id
	local dstaddr
	local node
	local csid
	local sid
	local rt

	for node in "${src_node}" "${dst_node}" "${decap_node}"; do
		check_node_name "${node}"
	done

	node_id="$(get_id_node "${dst_node}")"
	dstaddr="${UNDERLAY_HS_PREFIX}:${node_id}::2"

	if [[ "${enc_type}" == "srh" ]]; then
		for rt in ${end_nodes}; do
			check_node_name "${rt}"

			node_id="$(get_id_node "${rt}")"
			sid="$(printf "${SID_END_FMT}" "${node_id}")"

			sidlist="${sidlist},${sid}"
		done

		# decap node
		node_id="$(get_id_node "${decap_node}")"
		sid="$(printf "${SID_DT6_LEGACY_FMT}" "${node_id}")"

		sidlist="${sidlist},${sid}"
		# remove always the first ','
		sidlist="${sidlist#?}"

		# add the encap policy
		ip -netns "${src_node}" route add \
			"${dstaddr}" encap seg6 mode encap \
			segs "${sidlist}" \
			dev "${DUM_IFNAME}"
	elif [[ "${enc_type}" == "red" ]]; then
		carrier="${RT_LO_PREFIX}:"

		for rt in ${end_nodes}; do
			check_node_name "${rt}"

			node_id="$(get_id_node "${rt}")"
			csid="$(printf "${CSID_FUNC_FMT}" \
				       "${node_id}" "${END_FUNC}"):"

			carrier="${carrier}${csid}"
		done

		# decap node
		node_id="$(get_id_node "${decap_node}")"
		sid="$(printf "${CSID_FUNC_FMT}" \
			      "${node_id}" "${DT6_LEGACY_FUNC}")"

		carrier="${carrier}${sid}::"

		ip -netns "${src_node}" route add \
			"${dstaddr}" encap seg6 mode encap.red \
			segs "${carrier}" \
			dev "${DUM_IFNAME}"
	else
		echo "Invalid encap type: ${enc_type}"
		exit 1
	fi
}

setup_all_srv6_policies()
{

	# save the original IFS
	local OLDIFS="${IFS}"
	local src_node
	local dst_node
	local enc_type
	local end_nodes
	local decap_node
	local policy

	for policy in "${SRV6_POLICIES[@]}"; do
		IFS=',' read -r src_node dst_node enc_type \
				end_nodes decap_node  <<< "${policy}"

		setup_srv6_policy "${src_node}" "${dst_node}" "${enc_type}" \
				  "${end_nodes}" "${decap_node}"
	done

	# restore the IFS
	IFS="${OLDIFS}"
}

create_links()
{
	# save the original IFS
	local OLDIFS="${IFS}"
	local src_node
	local dst_node
	local link

	for link in "${LINK_PAIRS[@]}"; do
		IFS=',' read -r src_node dst_node <<< "${link}"

		check_node_name "${src_node}"
		check_node_name "${dst_node}"

		create_veth_links "${src_node}" "${dst_node}"
		setup_address_links "${src_node}" "${dst_node}"
	done

	# restore the IFS
	IFS="${OLDIFS}"
}

setup_topology()
{
	create_routers
	create_hosts

	create_links

	setup_all_rts_neigh_reachability
	setup_all_rt_routes

	setup_all_rts_sids
	setup_all_srv6_policies
}

setup_tmux()
{
	local twin

	# Create a new tmux session
	tmux new-session -d -s ${TMUX} -n host bash

	for twin in "${TMUX_WIN[@]}"; do
		tmux new-window \
			-t "${TMUX}" \
			-n ${twin} \
			ip netns exec ${twin} bash
	done

	tmux select-window -t :1
	tmux set-option -g mouse on
	tmux attach -t "${TMUX}"
}

setup()
{
	cleanup

	set +e
	trap cleanup EXIT
	set -e

	setup_topology
	setup_tmux

	echo ">>>build OK<<<"
}

setup

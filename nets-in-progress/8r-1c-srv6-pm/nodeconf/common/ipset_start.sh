#!/bin/bash

# Available colors
export RED_COLOR_CODE='0x1'
export BLUE_COLOR_CODE='0x2'

# +-----------------+
# |      Egress     |
# +-----------------+

# For iptables
export RED_CHAIN_OUT='red-out'
export BLUE_CHAIN_OUT='blue-out'

# For ipset
export RED_HT_OUT='red-ht-out'
export BLUE_HT_OUT='blue-ht-out'

ipset -N ${RED_HT_OUT} sr6hash counters
ipset -N ${BLUE_HT_OUT} sr6hash counters

ip6tables -N ${RED_CHAIN_OUT} -t mangle
ip6tables -N ${BLUE_CHAIN_OUT} -t mangle

ip6tables -A POSTROUTING -t mangle -m rt --rt-type 4 -j ${RED_CHAIN_OUT}
ip6tables -I POSTROUTING 1 -t mangle -m rt --rt-type 4 -j ${BLUE_CHAIN_OUT}

ip6tables -A ${RED_CHAIN_OUT} -t mangle 	\
	-m set --match-set ${RED_HT_OUT} dst 	\
	-j TOS --set-tos ${RED_COLOR_CODE}

ip6tables -A ${BLUE_CHAIN_OUT} -t mangle 	\
	-m set --match-set ${BLUE_HT_OUT} dst 	\
	-j TOS --set-tos ${BLUE_COLOR_CODE}

ip6tables -A ${RED_CHAIN_OUT} -t mangle -j ACCEPT
ip6tables -A ${BLUE_CHAIN_OUT} -t mangle -j ACCEPT


# TODO: End.OTP, which IPv6 address?

# +-----------------+
# |     Ingress     |
# +-----------------+

# For iptables
export RED_CHAIN_IN='red-in'
export BLUE_CHAIN_IN='blue-in'

# For ipset
export RED_HT_IN='red-ht-in'
export BLUE_HT_IN='blue-ht-in'

ipset -N ${RED_HT_IN} sr6hash counters
ipset -N ${BLUE_HT_IN} sr6hash counters

ip6tables -N ${RED_CHAIN_IN} -t mangle
ip6tables -N ${BLUE_CHAIN_IN} -t mangle

ip6tables -A PREROUTING -t mangle 					\
		-m rt --rt-type 4 -m tos --tos ${RED_COLOR_CODE} 	\
	-j ${RED_CHAIN_IN}

ip6tables -A PREROUTING -t mangle 					\
		-m rt --rt-type 4 -m tos --tos ${BLUE_COLOR_CODE} 	\
	-j ${BLUE_CHAIN_IN}

# XXX
# On the ingress path we will decap the packet, so the outer IPv6 will be
# discarded. Why do we want to clean the IPv6 dscp field?

ip6tables -A ${RED_CHAIN_IN} -t mangle 					\
	-m set --match-set ${RED_HT_IN} dst -j TOS --set-tos 0x00

ip6tables -A ${BLUE_CHAIN_IN} -t mangle 				\
	-m set --match-set ${BLUE_HT_IN} dst -j TOS --set-tos 0x00

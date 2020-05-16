#!/usr/bin/python3

import os
import sys

sys.path.append(os.path.abspath("/opt/srv6-pm-xdp-ebpf/srv6-pfplm"))

from xdp_srv6_pfplm_helper_user import EbpfException, EbpfPFPLM

def main(argv):
    if (len(argv) == 1):
        print_help()

    if (len(argv) == 4 and argv[1] == "load"):
        xdp_load(argv[2], argv[3])
    elif (len(argv) == 4 and argv[1] == "set_color"):
        xdp_set_color(argv[2], argv[3])
    elif (len(argv) == 3 and argv[1] == "get_color"):
        xdp_get_color(argv[2])
    elif (len(argv) == 4 and argv[1] == "add_flow"):
        xdp_add_flow(argv[2], argv[3])
    elif (len(argv) == 4 and argv[1] == "del_flow"):
        xdp_del_flow(argv[2], argv[3])
    elif (len(argv) == 5 and argv[1] == "get_flow_stats"):
        xdp_get_flow_stats(argv[2], argv[3], argv[4])
    elif (len(argv) == 3 and argv[1] == "unload"):
        xdp_unload(argv[2])
    else:
       print_help()

def print_help():
    print("error: invalid arguments")
    print()
    print("Help:")
    print("load                 <ifname> <igr|egr>")
    print("unload               <ifname>")
    print("set_color            <ifname> <color>")
    print("get_color            <ifname>")
    print("add_flow             <ifname> <segs>")
    print("del_flow             <ifname> <segs>")
    print("get_flow_stats       <ifname> <segs> <color>")
    exit(1)

def xdp_load(ifname, direction):
    try:
        obj = EbpfPFPLM()

        if (direction == "igr"):
            p_direction = obj.lib.XDP_PROG_DIR_INGRESS
        elif (direction == "egr"):
            p_direction = obj.lib.XDP_PROG_DIR_EGRESS
        else:
            print("wrong direction")
            exit(1)

        obj.pfplm_load(ifname, p_direction, obj.lib.F_VERBOSE | obj.lib.F_FORCE)
    except EbpfException as e:
        e.print_exception()
        exit(1)

def xdp_set_color(ifname, color):
    try:
        obj = EbpfPFPLM()
        obj.pfplm_change_active_color(ifname, int(color));
    except EbpfException as e:
        e.print_exception()
        exit(1)

def xdp_get_color(ifname):
    try:
        obj = EbpfPFPLM()
        color = obj.pfplm_get_active_color(ifname)
        print(color)
    except EbpfException as e:
        e.print_exception()
        exit(1)

def xdp_add_flow(ifname, segs):
    try:
        obj = EbpfPFPLM()
        obj.pfplm_add_flow(ifname, segs)
    except EbpfException as e:
        e.print_exception()
        exit(1)

def xdp_del_flow(ifname, segs):
    try:
        obj = EbpfPFPLM()
        obj.pfplm_del_flow(ifname, segs)
    except EbpfException as e:
        e.print_exception()
        exit(1)

def xdp_get_flow_stats(ifname, segs, color):
    try:
        obj = EbpfPFPLM()
        packets = obj.pfplm_get_flow_stats(ifname, segs, int(color))
        print(packets)
    except EbpfException as e:
        e.print_exception()
        exit(1)

def xdp_unload(ifname):
    try:
        obj = EbpfPFPLM()
        obj.pfplm_unload(ifname, obj.lib.F_VERBOSE | obj.lib.F_FORCE)
    except EbpfException as e:
        e.print_exception()
        exit(1)

if __name__ == "__main__":
   main(sys.argv[0:])

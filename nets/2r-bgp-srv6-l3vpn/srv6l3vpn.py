#!/usr/bin/python

# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring

import os
import shutil
from argparse import ArgumentParser

import python_hosts
from mininet.cli import CLI
# from mininet.link import Link
from mininet.log import setLogLevel
from mininet.net import Mininet
# from mininet.topo import Topo
from mininet.node import Host
from mininet.util import dumpNodeConnections

# BASEDIR = "/home/user/mytests/ospf3routers/nodeconf/"
BASEDIR = os.getcwd() + "/nodeconf/"
OUTPUT_PID_TABLE_FILE = "/tmp/pid_table_file.txt"

PRIVDIR = '/var/priv'

# Path of the file containing the entries (ip-hostname)
# to be added to /etc/hosts
ETC_HOSTS_FILE = './etc-hosts'

# Define whether to add Mininet nodes to /etc/hosts file or not
ADD_ETC_HOSTS = True


class BaseNode(Host):

    def __init__(self, name, *args, **kwargs):
        dirs = [PRIVDIR]
        Host.__init__(self, name, privateDirs=dirs, *args, **kwargs)
        self.dir = "/tmp/%s" % name
        self.nets = []
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)

    def config(self, **kwargs):
        # pylint: disable=arguments-differ

        # Init steps
        Host.config(self, **kwargs)
        # Iterate over the interfaces
        # first = True
        for intf in self.intfs.values():
            # Remove any configured address
            self.cmd('ifconfig %s 0' % intf.name)
            # # For the first one, let's configure the mgmt address
            # if first:
            #   first = False
            #   self.cmd('ip a a %s dev %s' %(kwargs['mgmtip'], intf.name))
        # let's write the hostname in /var/mininet/hostname
        self.cmd("echo '" + self.name + "' > " + PRIVDIR + "/hostname")
        if os.path.isfile(BASEDIR + self.name + "/start.sh"):
            self.cmd('source %s' % BASEDIR + self.name + "/start.sh")

    def cleanup(self):
        def remove_if_exists(filename):
            if os.path.exists(filename):
                os.remove(filename)

        Host.cleanup(self)
        # Rm dir
        if os.path.exists(self.dir):
            shutil.rmtree(self.dir)

        remove_if_exists(BASEDIR + self.name + "/zebra.pid")
        remove_if_exists(BASEDIR + self.name + "/zebra.log")
        remove_if_exists(BASEDIR + self.name + "/zebra.sock")
        remove_if_exists(BASEDIR + self.name + "/isis8d.pid")
        remove_if_exists(BASEDIR + self.name + "/isis8d.log")
        remove_if_exists(BASEDIR + self.name + "/isisd.log")
        remove_if_exists(BASEDIR + self.name + "/isisd.pid")

        remove_if_exists(OUTPUT_PID_TABLE_FILE)

        # if os.path.exists(BASEDIR+self.name+"/zebra.pid"):
        #     os.remove(BASEDIR+self.name+"/zebra.pid")

        # if os.path.exists(BASEDIR+self.name+"/zebra.log"):
        #     os.remove(BASEDIR+self.name+"/zebra.log")

        # if os.path.exists(BASEDIR+self.name+"/zebra.sock"):
        #     os.remove(BASEDIR+self.name+"/zebra.sock")

        # if os.path.exists(BASEDIR+self.name+"/ospfd.pid"):
        #     os.remove(BASEDIR+self.name+"/ospfd.pid")

        # if os.path.exists(BASEDIR+self.name+"/ospfd.log"):
        #     os.remove(BASEDIR+self.name+"/ospfd.log")

        # if os.path.exists(OUTPUT_PID_TABLE_FILE):
        #     os.remove(OUTPUT_PID_TABLE_FILE)


class Router(BaseNode):
    def __init__(self, name, *args, **kwargs):
        BaseNode.__init__(self, name, *args, **kwargs)

# the add_link function creates a link and assigns the interface names
# as node1-node2 and node2-node1


def add_link(my_net, node1, node2):
    my_net.addLink(node1, node2, intfName1=node1.name + '-' + node2.name,
                   intfName2=node2.name + '-' + node1.name)


def create_topo(my_net):
    # pylint: disable=invalid-name, too-many-locals

    h11 = my_net.addHost(name='h11', cls=BaseNode)
    h12 = my_net.addHost(name='h12', cls=BaseNode)
    h13 = my_net.addHost(name='h13', cls=BaseNode)

    h21 = my_net.addHost(name='h21', cls=BaseNode)
    h22 = my_net.addHost(name='h22', cls=BaseNode)
    h23 = my_net.addHost(name='h23', cls=BaseNode)

    pe1 = my_net.addHost(name='pe1', cls=Router)
    pe2 = my_net.addHost(name='pe2', cls=Router)

    # note that if the interface names are not provided,
    # the order of adding link will determine the
    # naming of the interfaces (e.g. on r1: r1-eth0, r1-eth1, r1-eth2...)
    # it is possible to provide names as follows
    # Link(h1, r1, intfName1='h1-eth0', intfName2='r1-eth0')
    # the add_link function creates a link and assigns the interface names
    # as node1-node2 and node2-node1

    # hosts of pe1
    add_link(my_net, h11, pe1)
    add_link(my_net, h12, pe1)
    add_link(my_net, h13, pe1)
    # pe1 - pe2
    add_link(my_net, pe1, pe2)
    # hosts of pe2
    add_link(my_net, h21, pe2)
    add_link(my_net, h22, pe2)
    add_link(my_net, h23, pe2)

    # Setup VRFs
    pe1.cmd('ip link add red type vrf table 10')
    pe1.cmd('ip link add green type vrf table 20')
    pe1.cmd('ip link set red up')
    pe1.cmd('ip link set green up')
    pe1.cmd('ip link set pe1-h11 master green')
    pe1.cmd('ip link set pe1-h12 master green')
    pe1.cmd('ip link set pe1-h13 master red')

    pe2.cmd('ip link add red type vrf table 10')
    pe2.cmd('ip link add green type vrf table 20')
    pe2.cmd('ip link set red up')
    pe2.cmd('ip link set green up')
    pe2.cmd('ip link set pe2-h21 master green')
    pe2.cmd('ip link set pe2-h22 master red')
    pe2.cmd('ip link set pe2-h23 master red')


def add_nodes_to_etc_hosts():
    # Get /etc/hosts
    etc_hosts = python_hosts.hosts.Hosts()
    # Import host-ip mapping defined in etc-hosts file
    count = etc_hosts.import_file(ETC_HOSTS_FILE)
    # Print results
    count = count['add_result']['ipv6_count'] + \
        count['add_result']['ipv4_count']
    print('*** Added %s entries to /etc/hosts\n' % count)


def remove_nodes_from_etc_hosts(net):
    print('*** Removing entries from /etc/hosts\n')
    # Get /etc/hosts
    etc_hosts = python_hosts.hosts.Hosts()
    for host in net.hosts:
        # Remove all the nodes from /etc/hosts
        etc_hosts.remove_all_matching(name=str(host))
    # Write changes to /etc/hosts
    etc_hosts.write()


def stop_all():
    # Clean Mininet emulation environment
    os.system('sudo mn -c')
    # Kill all the started daemons
    os.system('sudo killall sshd zebra isisd staticd bgpd')


def extract_host_pid(dumpline):
    temp = dumpline[dumpline.find('pid=') + 4:]
    return int(temp[:len(temp) - 2])


def simple_test():
    "Create and test a simple network"

    # topo = RoutersTopo()
    # net = Mininet(topo=topo, build=False, controller=None)
    net = Mininet(topo=None, build=False, controller=None)
    create_topo(net)

    net.build()
    net.start()

    print("Dumping host connections")
    dumpNodeConnections(net.hosts)
    # print "Testing network connectivity"
    # net.pingAll()

    with open(OUTPUT_PID_TABLE_FILE, "w") as file:
        for host in net.hosts:
            file.write("%s %d\n" % (host, extract_host_pid(repr(host))))

    # Add Mininet nodes to /etc/hosts
    if ADD_ETC_HOSTS:
        add_nodes_to_etc_hosts()

    CLI(net)

    # Remove Mininet nodes from /etc/hosts
    if ADD_ETC_HOSTS:
        remove_nodes_from_etc_hosts(net)

    net.stop()
    stop_all()


def parse_arguments():
    # Get parser
    parser = ArgumentParser(
        description='Emulation of a Mininet topology (8 routers running '
                    'IS-IS, 1 controller out-of-band'
    )
    parser.add_argument(
        '--no-etc-hosts', dest='add_etc_hosts',
        action='store_false', default=True,
        help='Define whether to add Mininet nodes to /etc/hosts file or not'
    )
    # Parse input parameters
    args = parser.parse_args()
    # Return the arguments
    return args


def __main():
    global ADD_ETC_HOSTS  # pylint: disable=global-statement
    # Parse command-line arguments
    args = parse_arguments()
    # Define whether to add Mininet nodes to /etc/hosts file or not
    ADD_ETC_HOSTS = args.add_etc_hosts
    # Tell mininet to print useful information
    setLogLevel('info')
    simple_test()


if __name__ == '__main__':
    __main()

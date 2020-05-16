#!/usr/bin/python

import os

# Activate virtual environment if a venv path has been specified in .venv
# This must be executed only if this file has been executed as a 
# script (instead of a module)
if __name__ == '__main__':
    # Check if .venv file exists
    if os.path.exists('.venv'):
        with open('.venv', 'r') as venv_file:
            # Get virtualenv path from .venv file
            venv_path = venv_file.read()
        # Get path of the activation script
        venv_path = os.path.join(venv_path, 'bin/activate_this.py')
        if not os.path.exists(venv_path):
            print('Virtual environment path specified in .venv '
                  'points to an invalid path\n')
            exit(-2)
        with open(venv_path) as f:
            # Read the activation script
            code = compile(f.read(), venv_path, 'exec')
            # Execute the activation script to activate the venv
            exec(code, {'__file__': venv_path})

from argparse import ArgumentParser
import shutil
from dotenv import load_dotenv
from mininet.topo import Topo
from mininet.node import Host, OVSBridge
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.util import dumpNodeConnections
from mininet.link import Link
from mininet.log import setLogLevel

#BASEDIR = "/home/user/mytests/ospf3routers/nodeconf/"
BASEDIR = os.getcwd()+"/nodeconf/"
OUTPUT_PID_TABLE_FILE = "/tmp/pid_table_file.txt"

PRIVDIR = '/var/priv'

START_NODE_MANAGERS = False

# Load environment variables from .env file
load_dotenv()

# Get node manager path
NODE_MANAGER_PATH = os.getenv('NODE_MANAGER_PATH', None)
if NODE_MANAGER_PATH is not None:
    NODE_MANAGER_PATH = os.path.join(NODE_MANAGER_PATH,
                                     'srv6_manager.py')
# Get gRPC server port
NODE_MANAGER_GRPC_PORT = os.getenv('NODE_MANAGER_GRPC_PORT', None)


class BaseNode(Host):

    def __init__(self, name, *args, **kwargs):
        dirs = [PRIVDIR]
        Host.__init__(self, name, privateDirs=dirs, *args, **kwargs)
        self.dir = "/tmp/%s" % name
        self.nets = []
        if not os.path.exists(self.dir):
            os.makedirs(self.dir) 

    def config(self, **kwargs):
        # Init steps
        Host.config(self, **kwargs)
        # Iterate over the interfaces
        first = True
        for intf in self.intfs.values():
            # Remove any configured address
            self.cmd('ifconfig %s 0' %intf.name)
            # # For the first one, let's configure the mgmt address
            # if first:
            #   first = False
            #   self.cmd('ip a a %s dev %s' %(kwargs['mgmtip'], intf.name))
        #let's write the hostname in /var/mininet/hostname
        self.cmd("echo '" + self.name + "' > "+PRIVDIR+"/hostname")
        if os.path.isfile(BASEDIR+self.name+"/start.sh") :
            self.cmd('source %s' %BASEDIR+self.name+"/start.sh")

    def cleanup(self):
        def remove_if_exists (filename):
            if os.path.exists(filename):
                os.remove(filename)

        Host.cleanup(self)
        # Rm dir
        if os.path.exists(self.dir):
            shutil.rmtree(self.dir)

        remove_if_exists(BASEDIR+self.name+"/zebra.pid")
        remove_if_exists(BASEDIR+self.name+"/zebra.log")
        remove_if_exists(BASEDIR+self.name+"/zebra.sock")
        remove_if_exists(BASEDIR+self.name+"/isis8d.pid")
        remove_if_exists(BASEDIR+self.name+"/isis8d.log")
        remove_if_exists(BASEDIR+self.name+"/isisd.log")
        remove_if_exists(BASEDIR+self.name+"/isisd.pid")

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

    def config(self, **kwargs):
        # Init steps
        BaseNode.config(self, **kwargs)
        # Start node managers
        if START_NODE_MANAGERS:
            self.cmd('python %s --grpc-port %s &'
                     % (NODE_MANAGER_PATH, NODE_MANAGER_GRPC_PORT))


class Switch(OVSBridge):
    def __init__(self, name, *args, **kwargs):
        dirs = [PRIVDIR]
        OVSBridge.__init__(self, name, *args, **kwargs)
        self.dir = "/tmp/%s" % name
        self.nets = []
        if not os.path.exists(self.dir):
            os.makedirs(self.dir) 

    def config(self, **kwargs):
        # Init steps
        OVSBridge.config(self, **kwargs)
        # Iterate over the interfaces
        for intf in self.intfs.itervalues():
            # Remove any configured address
            self.cmd('ifconfig %s 0' %intf.name)
            # # For the first one, let's configure the mgmt address
            # if first:
            #   first = False
            #   self.cmd('ip a a %s dev %s' %(kwargs['mgmtip'], intf.name))
        #let's write the hostname in /var/mininet/hostname
        self.cmd("echo '" + self.name + "' > "+PRIVDIR+"/hostname")
        if os.path.isfile(BASEDIR+self.name+"/start.sh") :
            self.cmd('source %s' %BASEDIR+self.name+"/start.sh")

    def cleanup(self):
        def remove_if_exists (filename):
            if os.path.exists(filename):
                os.remove(filename)

        OVSBridge.cleanup(self)
        # Rm dir
        if os.path.exists(self.dir):
            shutil.rmtree(self.dir)


# the add_link function creates a link and assigns the interface names
# as node1-node2 and node2-node1
def add_link (my_net, node1, node2):
    my_net.addLink(node1, node2, intfName1=node1.name+'-'+node2.name,
                       intfName2=node2.name+'-'+node1.name)

def create_topo(my_net):
    h11 = my_net.addHost(name='h11', cls=BaseNode)
    h12 = my_net.addHost(name='h12', cls=BaseNode)
    h13 = my_net.addHost(name='h13', cls=BaseNode)

    h31 = my_net.addHost(name='h31', cls=BaseNode)
    h32 = my_net.addHost(name='h32', cls=BaseNode)
    h33 = my_net.addHost(name='h33', cls=BaseNode)

    h51 = my_net.addHost(name='h51', cls=BaseNode)
    h52 = my_net.addHost(name='h52', cls=BaseNode)
    h53 = my_net.addHost(name='h53', cls=BaseNode)

    h81 = my_net.addHost(name='h81', cls=BaseNode)
    h82 = my_net.addHost(name='h82', cls=BaseNode)
    h83 = my_net.addHost(name='h83', cls=BaseNode)

    hdc1 = my_net.addHost(name='hdc1', cls=BaseNode)
    hdc2 = my_net.addHost(name='hdc2', cls=BaseNode)
    hdc3 = my_net.addHost(name='hdc3', cls=BaseNode)

    controller = my_net.addHost(name='controller', cls=BaseNode,
                                sshd=False, inNamespace=False)

    r1 = my_net.addHost(name='r1', cls=Router)
    r2 = my_net.addHost(name='r2', cls=Router)
    r3 = my_net.addHost(name='r3', cls=Router)
    r4 = my_net.addHost(name='r4', cls=Router)
    r5 = my_net.addHost(name='r5', cls=Router)
    r6 = my_net.addHost(name='r6', cls=Router)
    r7 = my_net.addHost(name='r7', cls=Router)
    r8 = my_net.addHost(name='r8', cls=Router)

    #note that if the interface names are not provided,
    #the order of adding link will determine the
    #naming of the interfaces (e.g. on r1: r1-eth0, r1-eth1, r1-eth2...)
    # it is possible to provide names as follows
    # Link(h1, r1, intfName1='h1-eth0', intfName2='r1-eth0')
    # the add_link function creates a link and assigns the interface names
    # as node1-node2 and node2-node1

    #hosts of r1
    add_link(my_net, h11,r1)
    add_link(my_net, h12,r1)
    add_link(my_net, h13,r1)
    #r1 - r2
    add_link(my_net, r1,r2)
    #datacenters of r2
    add_link(my_net, hdc1,r2)
    #r2 - r3
    add_link(my_net, r2,r3)
    #r2 - r7
    add_link(my_net, r2,r7)
    #hosts of r3
    add_link(my_net, h31,r3)
    add_link(my_net, h32,r3)
    add_link(my_net, h33,r3)
    #r3 - r4
    add_link(my_net, r3,r4)
    #r4 - r5
    add_link(my_net, r4,r5)
    #r4 - r6
    add_link(my_net, r4,r6)
    #hosts of r5
    add_link(my_net, h51,r5)
    add_link(my_net, h52,r5)
    add_link(my_net, h53,r5)
    #datacenters of r5
    add_link(my_net, hdc3,r5)
    #r5 - r6
    add_link(my_net, r5,r6)
    #r6 - r7
    add_link(my_net, r6,r7)
    #r6 - r8
    add_link(my_net, r6,r8)
    #r7 - r8
    add_link(my_net, r7,r8)
    #hosts of r8
    add_link(my_net, h81,r8)
    add_link(my_net, h82,r8)
    add_link(my_net, h83,r8)
    #datacenters of r8
    add_link(my_net, hdc2,r8)

    # Create the mgmt switch
    sw = my_net.addSwitch(name='sw', cls=Switch, dpid='1')
    # Create a link between mgmt switch and controller
    add_link(my_net, controller, sw)
    # Connect all the routers to the management network
    add_link(my_net, r1, sw)
    add_link(my_net, r2, sw)
    add_link(my_net, r3, sw)
    add_link(my_net, r4, sw)
    add_link(my_net, r5, sw)
    add_link(my_net, r6, sw)
    add_link(my_net, r7, sw)
    add_link(my_net, r8, sw)


def stopAll():
    # Clean Mininet emulation environment
    os.system('sudo mn -c')
    # Kill all the started daemons
    os.system('sudo killall sshd zebra isisd')

def extractHostPid (dumpline):
    temp = dumpline[dumpline.find('pid=')+4:]
    return int(temp [:len(temp)-2])


    
def simpleTest():
    "Create and test a simple network"

    #topo = RoutersTopo()
    #net = Mininet(topo=topo, build=False, controller=None)
    net = Mininet(topo=None, build=False, controller=None)
    create_topo(net)

    net.build()
    net.start()


    print("Dumping host connections")
    dumpNodeConnections(net.hosts)
    #print "Testing network connectivity"
    #net.pingAll()

    with open(OUTPUT_PID_TABLE_FILE,"w") as file:
        for host in net.hosts:
            file.write("%s %d\n" % (host, extractHostPid( repr(host) )) )

    CLI( net ) 
    net.stop() 
    stopAll()


def parse_arguments():
    # Get parser
    parser = ArgumentParser(
        description='Emulation of a Mininet topology (8 routers running '
                    'IS-IS, 1 controller out-of-band'
    )
    parser.add_argument(
        '--start-node-managers', dest='start_node_managers',
        action='store_true', default=False,
        help='Define whether to start node manager on routers or not'
    )
    # Parse input parameters
    args = parser.parse_args()
    # Return the arguments
    return args


if __name__ == '__main__':
    # Parse command-line arguments
    args = parse_arguments()
    # Define whether to start node manager on routers or not 
    START_NODE_MANAGERS = args.start_node_managers
    if START_NODE_MANAGERS:
        if NODE_MANAGER_PATH is None:
            print('Error: --start-node-managers requires NODE_MANAGER_PATH '
                'variable')
            print('NODE_MANAGER_PATH variable not set in .env file\n')
            exit(-2)
        if not os.path.exists(NODE_MANAGER_PATH):
            print('Error: --start-node-managers requires NODE_MANAGER_PATH '
                'variable')
            print('NODE_MANAGER_PATH defined in .env file '
                  'points to a non existing folder\n')
            exit(-2)
        if NODE_MANAGER_GRPC_PORT is None:
            print('Error: --start-node-managers requires '
                  'NODE_MANAGER_GRPC_PORT variable')
            print('NODE_MANAGER_GRPC_PORT variable not set in .env file\n')
            exit(-2)
    # Tell mininet to print useful information
    setLogLevel('info')
    simpleTest()

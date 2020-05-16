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
            # and remove trailing newline chars
            venv_path = venv_file.read().rstrip()
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

import shutil
from mininet.topo import Topo
from mininet.node import Host
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.util import dumpNodeConnections
from mininet.link import Link
from mininet.log import setLogLevel

#BASEDIR = "/home/user/mytests/ospf3routers/nodeconf/"
BASEDIR = os.getcwd()+"/nodeconf/"
OUTPUT_PID_TABLE_FILE = "/tmp/pid_table_file.txt"

PRIVDIR = '/var/priv'

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
        remove_if_exists(BASEDIR+self.name+"/ospfd.pid")
        remove_if_exists(BASEDIR+self.name+"/ospfd.log")
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
def add_link (node1, node2):
    Link(node1, node2, intfName1=node1.name+'-'+node2.name,
                       intfName2=node2.name+'-'+node1.name)

def create_topo(my_net):
    h1 = my_net.addHost(name='h1', cls=BaseNode)
    h2 = my_net.addHost(name='h2', cls=BaseNode)
    h3 = my_net.addHost(name='h3', cls=BaseNode)
    r1 = my_net.addHost(name='r1', cls=Router)
    r2 = my_net.addHost(name='r2', cls=Router)
    r3 = my_net.addHost(name='r3', cls=Router)

    #note that if the interface names are not provided,
    #the order of adding link will determine the
    #naming of the interfaces (e.g. on r1: r1-eth0, r1-eth1, r1-eth2...)
    # it is possible to provide names as follows
    # Link(h1, r1, intfName1='h1-eth0', intfName2='r1-eth0')
    # the add_link function creates a link and assigns the interface names
    # as node1-node2 and node2-node1

    #Link(h1, r1, intfName1='h1-r1', intfName2='r1-h1')
    #Link(h2, r2, intfName1='h2-r2', intfName2='r2-h2')
    #Link(h3, r3, intfName1='h3-r3', intfName2='r3-h3')
    add_link(h1,r1)
    add_link(h2,r2)
    add_link(h3,r3)

    add_link(r1,r2)
    add_link(r1,r3)
    add_link(r2,r3)


def stopAll():
    # Clean Mininet emulation environment
    os.system('sudo mn -c')
    # Kill all the started daemons
    os.system('sudo killall sshd zebra ospfd')

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



if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    simpleTest()
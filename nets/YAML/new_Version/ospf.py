#!/usr/bin/python

import os
import shutil
from mininet.topo import Topo
from mininet.node import Host
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.util import dumpNodeConnections
from mininet.link import Link
from mininet.log import setLogLevel
from mininet.link import TCLink

BASEDIR = os.getcwd()+"/nodeconf/"
OUTPUT_PID_TABLE_FILE = "/tmp/pid_table_file.txt"

PRIVDIR = '/var/priv'

class BaseNode(Host):

	def __init__(self, name, *args, **kwargs):
		dirs = [PRIVDIR]
		Host.__init__(self, name, privateDirs=dirs, *args, **kwargs)
		self.dir = "/temp/%s" %name
		self.nets = []
		if not os.path.exists(self.dir):
			os.makedirs(self.dir)

	def config(self, **kwargs):
		#Init steps
		Host.config(self, **kwargs)
		# Iterate over the interfaces
		first = True
		for intf in self.intfs.itervalues():
			# Remove any configured address
			self.cmd('ifconfig %s 0' %intf.name)
		# hostnames in /var/mininet/hostname
		self.cmd("echo '" + self.name + "' > "+PRIVDIR+"/hostname")
		if os.path.isfile(BASEDIR+self.name+"/start.sh"):
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
		remove_if_exists(BASEDIR+self.name+"/ospf6d.pid")
		remove_if_exists(BASEDIR+self.name+"/ospf6d.log")

		remove_if_exists(OUTPUT_PID_TABLE_FILE)

class Router(BaseNode):
	def __init__(self, name, *args, **kwargs):
		BaseNode.__init__(self, name, *args, **kwargs)

# the add_link function creates a link and assigns the interface names
# as node1-node2 and node2-node1
def add_link (node1, node2):
	Link(node1, node2, intfName1=node1.name+'-'+node2.name,
				intfName2=node2.name+'-'+node1.name)

def create_topo(my_net):
	h11 = my_net.addHost(name='h11', cls=BaseNode)
	h12 = my_net.addHost(name='h12', cls=BaseNode)
	h21 = my_net.addHost(name='h21', cls=BaseNode)
	r1 = my_net.addHost(name='r1', cls=Router)
	r2 = my_net.addHost(name='r2', cls=Router)
	add_link(h11,r1)
	add_link(h12,r1)
	add_link(h21,r2)
	add_link(r1,r2)
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


	print "Dumping host connections"
	dumpNodeConnections(net.hosts)
	#print 'Testing network connectivity'
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
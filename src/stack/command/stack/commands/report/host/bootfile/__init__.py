#
# @SI_COPYRIGHT@
# @SI_COPYRIGHT@
#

import os
import stack.commands
from stack.exception import *
import struct
import socket

from itertools import groupby
from operator import itemgetter


class Command(stack.commands.Command,
	stack.commands.HostArgumentProcessor):
	"""
	Output the PXE file for a host
	<arg name="host" type="string" repeat="1">
	One or more hostnames
	</arg>
	<param name="action" type="string" optional="0">
	Generate PXE file for a specified action
	</param>
	"""
	def getHostHexIP(self, host):
		"""
		Return list of IP's (in hex format) for each interface where pxe=true for `host`
		"""
		hex_ip_list = []
		for iface in self.host_interfaces[host]:
			if iface['ip'] and iface['pxe']:
				# Compute the HEX IP filename for the host
				# inet_aton('a.b.c.d') -> binary (bytes) repr of (long) int
				# struct unpacks that into a python Long, which we then cast to a hex value
				hex_ip_list.append("%08X" % struct.unpack('!L', socket.inet_aton(iface['ip']))[0])
		return hex_ip_list

	def getBootParams(self, host, action):
		for row in self.call('list.host', [ host ]):
			if action == 'install':
				bootaction = row['installaction']
			else:
				bootaction = row['runaction']

		kernel = ramdisk = args = None
		for row in self.call('list.bootaction'):
			if row['action'] == bootaction:
				kernel  = row['kernel']
				ramdisk = row['ramdisk']
				args    = row['args']
		return (kernel, ramdisk, args)

	def run(self, params, args):
		# Get a list of hosts
		hosts = self.getHostnames(args, managed_only=True)

		(action, ) = self.fillParams([
			('action',None)])

		# since we'll look up iface data for every host in 'hosts' anyway, get it all at once
		# stored as a class-level variable in a dict[hostname] -> [list of iface dicts]
		self.host_interfaces = dict(
			(k,list(v)) for k,v in groupby(
			self.call('list.host.interface', hosts + ['expanded=True']),
			itemgetter('host')
			))

		self.beginOutput()
		self.runPlugins([hosts, action])
		self.endOutput(padChar='', trimOwner=(len(hosts) == 1))


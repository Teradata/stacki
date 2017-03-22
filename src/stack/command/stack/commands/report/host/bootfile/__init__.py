#
# @SI_COPYRIGHT@
# @SI_COPYRIGHT@
#

import os
import stack.commands
from stack.exception import *

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
		#
		# Get the IP and NETMASK of the host
		#
	
		appliance = self.getHostAttr(host, 'appliance')
		if appliance == 'frontend':
			return None

		for row in self.call('list.host.interface', [host, 'expanded=True']):
			ip = row['ip']
			pxe = row['pxe']
			if ip and pxe:
				#
				# Compute the HEX IP filename for the host
				#
				hexstr = ''
				for i in string.split(ip, '.'):
					hexstr += '%02x' % (int(i))

				return hexstr.upper()

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

		self.beginOutput()
		self.runPlugins([hosts, action])
		self.endOutput(padChar='', trimOwner=(len(hosts) == 1))


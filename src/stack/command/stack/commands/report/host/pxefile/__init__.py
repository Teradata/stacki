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
	def getHostPXEInfo(self, host, action):
		#
		# Get the IP and NETMASK of the host
		#
	
		appliance = self.db.getHostAttr(host, 'appliance')
		if appliance == 'frontend':
			filename = '/tftpboot/pxelinux/pxelinux.cfg/default'
			action = 'os'
			return (host, action, filename, None, None, None)

		for row in self.call('list.host.interface', [host, 'expanded=True']):
			ip = row['ip']
			if ip:
				#
				# Compute the HEX IP filename for the host
				#
				filename = '/tftpboot/pxelinux/pxelinux.cfg/'
				hexstr = ''
				for i in string.split(ip, '.'):
					hexstr += '%02x' % (int(i))
				filename += '%s' % hexstr.upper()

				return (host, action, filename,
					ip, row['mask'], row['gateway'])

	def run(self, params, args):
		# Get a list of hosts
		hosts = self.getHostnames(args, managed_only=True)

		(action, ) = self.fillParams([
			('action',None)])

		self.beginOutput()
		for host in hosts:
			osname = self.db.getHostOS(host)
			# If actions aren't specified on the command line
			# get info from the database
			if not action:
				o = self.call('list.host.boot',[host])
				action = o[0]['action']
			# Run the OS-specific implementation
			pxeInfo = self.getHostPXEInfo(host, action)
			self.runImplementation(osname, pxeInfo)
		self.endOutput(padChar='')

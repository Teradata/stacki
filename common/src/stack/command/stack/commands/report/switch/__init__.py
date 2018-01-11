# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
# 

import re
import stack.commands
from stack.switch import SwitchDellX1052 as switch


class command(stack.commands.HostArgumentProcessor,
	stack.commands.report.command,
	stack.commands.DatabaseConnection):
	pass

class Command(command):
	"""
	Output the switch configuration file.
	"""

	def run(self, params, args):

		self.beginOutput()


		#hosts = self.getHostnames(args)
		for switch in self.call('list.switch'):
		#	osname = self.getHostAttr(host, 'os')
		#	self.runImplementation(osname, [host])
			switch_interface, *xargs = self.call('list.host.interface', [switch['host']])
			switch_network = switch_interface['network']
			frontend = self.db.getHostname('localhost')
			hosts = self.db.select("""
			* 
			from switch_connections s
			where s.switch=(select id from nodes where name='%s')
			""" % switch['host'])

			self.addOutput(frontend, '<stack:file stack:name="/tftpboot/pxelinux/x1052_temp_upload">')
			for (host, interface, switch, port, subnet, vlan) in hosts:
				#attr = self.getHostAttr(host, 'appliance')
				attr = 'frontends'
				if attr == 'frontend':
					self.addOutput(frontend, '!')
					self.addOutput(frontend, 'interface gigabitethernet1/0/%s' % port)
					self.addOutput(frontend,'  switchport mode general')
					self.addOutput(frontend,'  switchport general allowed vlan add %s tagged' % vlan)
					self.addOutput(frontend,'  switchport general allowed vlan add 1 untagged')
				else:
					self.addOutput(frontend, '!')
					self.addOutput(frontend, 'interface gigabitethernet1/0/%s' % port)
					self.addOutput(frontend, ' switchport access vlan %s' % vlan)
		
			self.addOutput(frontend, '!')
			self.addOutput(frontend, '</stack:file>')
		self.endOutput(padChar='', trimOwner=True)


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

	<example cmd='report switch'>
	Outputs data for /tftpboot/pxelunux/upload
	</example>
	"""

	def run(self, params, args):

		self.beginOutput()


		#hosts = self.getHostnames(args)
		for switch in self.call('list.switch', args):
		#	osname = self.getHostAttr(host, 'os')
		#	self.runImplementation(osname, [host])
			frontend = self.db.getHostname('localhost')
			hosts = self.db.select("""
			n.name, s.port, i.vlanid
			from switchports s, nodes n, nodes sw, subnets sub, networks i
			where i.node = n.id
			and s.switch = sw.id
			and i.subnet = sub.id
			and s.interface = i.id
			and s.switch = (select id from nodes where name='%s')
			""" % switch['switch'])

			self.addOutput(frontend, '<stack:file stack:name="/tftpboot/pxelinux/%s_upload">' % switch['switch'])

			# Set blank vlan from 2-50
			self.addOutput(frontend, 'vlan 2-50')
			for (host, port, vlan) in hosts:
				attr = self.getHostAttr(host, 'appliance')

				# if vlan isn't set, set vlan to '1'
				if not vlan:
					vlan = '1'

				if attr == 'frontend':
					self.addOutput(frontend, '!')
					self.addOutput(frontend, 'interface gigabitethernet1/0/%s' % port)
					self.addOutput(frontend,'  switchport mode general')
					self.addOutput(frontend,'  switchport general allowed vlan add 2-100 tagged')
					self.addOutput(frontend,'  switchport general allowed vlan add 1 untagged')
				else:
					self.addOutput(frontend, '!')
					self.addOutput(frontend, 'interface gigabitethernet1/0/%s' % port)
					self.addOutput(frontend, ' switchport access vlan %s' % vlan)
		
			self.addOutput(frontend, '!')
			self.addOutput(frontend, '</stack:file>')
		self.endOutput(padChar='', trimOwner=True)


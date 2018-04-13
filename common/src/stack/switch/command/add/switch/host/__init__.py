# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgUnique, CommandError

class command(stack.commands.SwitchArgumentProcessor,
	      stack.commands.HostArgumentProcessor,
	      stack.commands.add.switch.command):
	pass

class Command(command):
	"""
	Add a new host to a switch

	<arg type='string' name='switch' optional='0' repeat='0'>
	Name of the switch
	</arg>

	<param type='string' name='host' optional='0'>
	Name of the host being assigned a vlan id
	</param>

	<param type='string' name='port' optional='0'>
	Port the host is connected to the switch on
	</param>

	<param type='string' name='interface' optional='1'>
	Name of the interface you want to use to connect to the switch.
	Default: The first interface that is found that shares the
	same network as the switch.
	</param>

	<example cmd='add switch host switch-0 host=backend-0 port=20'>
	Add host backend-0 to switch-0 connected to port 20
	</example>
	"""

	def run(self, params, args):

		host, port, interface, = self.fillParams([
			('host', None, True),
			('port', None, True),
			('interface', None, False),
			])
		switches = self.getSwitchNames(args)
		if len(switches) > 1:
			raise ArgUnique(self, 'switch')

		# Check if host exists
		hosts = self.getHostnames([host])

		for switch in switches:
			# Make sure switch has an interface
			if self.getSwitchNetwork(switch):
				self.addSwitchHost(switch, host, port, interface)
			else:
				raise CommandError(self,
					"switch '%s' doesn't have an interface" % switch)

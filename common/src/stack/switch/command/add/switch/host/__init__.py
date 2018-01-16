# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands.set.switch
from stack.exception import ArgUnique

class command(stack.commands.SwitchArgumentProcessor,
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

	<param type='string' name='vlan' optional='1'>
	Vlan ID to be set on the switch
	</param>
	
	<example cmd='add switch host switch-0 host=backend-0 port=20 vlan=2'>
	Add host backend-0 to switch-2 connected to port 20 with vlan 2
	</example>
	"""

	def run(self, params, args):

		host, port, vlan = self.fillParams([
			('host', None, True),
			('port', None, True),
			('vlan', '1'),
			])
		switches = self.getSwitchNames(args)
		if len(switches) > 1:
			raise ArgUnique(self, 'switch')

		for switch in switches:
			self.addSwitchHost(switch, host, port, vlan)

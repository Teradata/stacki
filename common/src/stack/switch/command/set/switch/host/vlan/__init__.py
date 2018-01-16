# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands.set.switch
from stack.exception import ArgUnique


class Command(stack.commands.set.switch.command):
	"""
	Sets the vlan id for a host to be configured on the switch.  

	<arg type='string' name='switch' optional='0' repeat='0'>
	Name of the switch
	</arg>
	
	<param type='string' name='host' optional='0'>
	Name of the host being assigned a vlan id
	</param>

	<param type='string' name='vlan' optional='0'>
	Vlan ID to be set on the switch
	</param>
	
	<example cmd='set switch host vlan switch-0 host=backend-0 vlan=2'>
	Sets the vlan of host backend-0 on switch-0 to 2
	</example>
	"""

	def run(self, params, args):

		host, vlan = self.fillParams([
			('host', None, True),
			('vlan', None, True),
			])
		switches = self.getSwitchNames(args)
		print(switches, host, vlan)
		if len(switches) > 1:
			raise ArgUnique(self, 'switch')

		for switch in switches:
			self.setSwitchHostVlan(switch, host, vlan)

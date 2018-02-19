# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import stack.commands
from stack.exception import ParamRequired, ParamType, ArgUnique, CommandError

class command(stack.commands.SwitchArgumentProcessor,
	stack.commands.add.command):
	pass

class Command(command):
	"""
	Adds an interface to a switch and sets the associated values.

	<arg type='string' name='switch'>
	Host name of machine
	</arg>
	
	<param type='string' name='interface'>
	The interface name on the switch (e.g., 'eth0', 'eth1')
	</param>

	<param type='string' name='ip'>
	The IP address to assign to the interface (e.g., '192.168.1.254')
	</param>

	<param type='string' name='network'>
	The name of the network to assign to the interface (e.g., 'private')
	</param>
	
	<param type='string' name='name'>
	The name to assign to the interface
	</param>
	
	<param type='string' name='mac'>
	The MAC address of the interface (e.g., '00:11:22:33:44:55')
	</param>
	
	<example cmd='add switch interface switch-0-0 interface=eth1 ip=192.168.1.2 network=private name=fast-0-0'>
	Add interface "eth1" to switch "switch-0-0" with the given
	IP address, network assignment, and name.
	</example>
	"""

	def run(self, params, args):

		switches = self.getSwitchNames(args)

		# Passthrough all the args and params to add.host.interface
		passthrough_params = list(map(
				     lambda x, y: "%s=%s" % (x, y),
				     params.keys(),
				     params.values()
				     ))

		# Call add host interface
		self.call('add.host.interface', switches + passthrough_params)

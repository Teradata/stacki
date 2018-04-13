# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands
from stack.exception import ParamRequired, ArgUnique


class Command(stack.commands.set.command):
	"""
	Sets the IP address for the named interface for one switch.

	<arg type='string' name='switch' required='1'>
	Switch name.
	</arg>
	
	<param type='string' name='interface'>
	Name of the interface.
	</param>

	<param type='string' name='mac'>
	MAC address of the interface.
	</param>

	<param type='string' name='ip' optional='0'>
	IP address
	</param>

	<example cmd='set switch interface ip switch-0-0 interface=eth1 ip=192.168.0.10'>
	Sets the IP Address for the eth1 device on host switch-0-0.
	</example>
	"""
	
	def run(self, params, args):
		
		passthrough_params = list(map(
				     lambda x, y: "%s=%s" % (x, y),
				     params.keys(),
				     params.values()
				     ))

		# Call set host interface ip
		self.command('set.host.interface.ip', args + passthrough_params)


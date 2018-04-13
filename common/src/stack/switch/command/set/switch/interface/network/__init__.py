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
from stack.exception import ParamRequired


class Command(stack.commands.set.command):
	"""
	Sets the network for named interface on one of more switches. 

	<arg type='string' name='switch' repeat='1' optional='0'>
	One or more named switches.
	</arg>
	
	<param type='string' name='interface'>
	Name of the interface.
	</param>

	<param type='string' name='mac'>
	MAC address of the interface.
	</param>

	<param type='string' name='network' optional='1'>
	The network address of the interface. This is a named network and must be
	listable by the command 'rocks list network'.
	</param>

	<example cmd='set host interface mac switch-0-0 interface=eth1 network=public'>
	Sets eth1 to be on the public network.
	</example>
	"""
	
	def run(self, params, args):

		passthrough_params = list(map(
				     lambda x, y: "%s=%s" % (x, y),
				     params.keys(),
				     params.values()
				     ))

		# Call set host interface name
		self.command('set.host.interface.name', args + passthrough_params)

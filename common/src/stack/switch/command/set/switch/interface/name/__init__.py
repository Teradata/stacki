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
from stack.exception import ParamType, ParamRequired, ArgUnique


class Command(stack.commands.set.command):
	"""
	Sets the logical name of a network interface on a particular switch.

	<arg type='string' name='switch'>
	Switch name.
	</arg>
	
	<param type='string' name='interface'>
	Name of the interface.
	</param>

	<param type='string' name='mac'>
	MAC address of the interface.
	</param>
	
	<param type='string' name='name' optional='0'>
	Name of this interface (e.g. newname). This is only the
	name associated with a certain interface. FQDNs are disallowed.
	To set the domain or zone for an interface, use the
	"stack add network" command, and then associate the interface
	with the network
	</param>

	<example cmd='set switch interface name switch-0-0 interface=eth1 name=cluster-0-0'>
	Sets the name for the eth1 device on host switch-0-0 to
	cluster-0-0.zonename. The zone is decided by the subnet that the
	interface is attached to.
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


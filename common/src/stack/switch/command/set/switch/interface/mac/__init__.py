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
from stack.exception import ArgRequired


class Command(stack.commands.set.command):
	"""
	Sets the mac address for named interface on switch.

	<arg type='string' name='switch' repeat='1'>
	Switch name.
	</arg>

	<param type='string' name='interface' optional='0'>
	Name of the interface.
	</param>

	<param type='string' name='mac' optional='0'>
	The mac address of the interface. Usually of the form dd:dd:dd:dd:dd:dd
	where d is a hex digit. This format is not enforced. Use mac=NULL to
	clear the mac address.
	</param>

	<example cmd='set switch interface mac switch-0-0 interface=eth1 mac=00:0e:0c:a7:5d:ff'>
	Sets the MAC Address for the eth1 device on host switch-0-0.
	</example>
	"""
	
	def run(self, params, args):

		passthrough_params = list(map(
				     lambda x, y: "%s=%s" % (x, y),
				     params.keys(),
				     params.values()
				     ))

		# Call set host interface mac
		self.command('set.host.interface.mac', args + passthrough_params)


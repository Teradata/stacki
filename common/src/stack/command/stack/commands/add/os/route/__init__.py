# @copyright@
# Copyright (c) 2006 - 2019 Teradata
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


class Command(stack.commands.add.os.command):
	"""
	Add a route for an OS type

	<arg type='string' name='os' repeat='1' optional='0'>
	The OS type (e.g., 'linux', 'sunos', etc.). This argument is required.
	</arg>

	<param type='string' name='address' optional='0'>
	Host or network address
	</param>

	<param type='string' name='gateway' optional='0'>
	Network (e.g., IP address), subnet name (e.g., 'private', 'public'), or
	a device gateway (e.g., 'eth0').
	</param>

	<param type='string' name='netmask'>
	Specifies the netmask for a network route.  For a host route
	this is not required and assumed to be 255.255.255.255
	</param>

	<param type='string' name='interface'>
	Specific interface to send traffic through. Should only be used if
	you need traffic to go through a VLAN interface (e.g., 'eth0.1').
	</param>
	"""

	def run(self, params, args):
		if len(args) == 0:
			raise ArgRequired(self, 'os')

		self.command('add.route', self._argv + ['scope=os'], verbose_errors = False)
		return self.rc

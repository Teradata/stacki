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


class Command(stack.commands.add.host.command):
	"""
	Add a route for a host

	<arg type='string' name='host' repeat='1' optional='0'>
	Host name of machine
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

	<param type='string' name='syncnow'>
	Add route to the routing table immediately
	</param>

	<example cmd="add host route localhost address=10.0.0.2 gateway=10.0.0.1 interface=eth1.2 syncnow=true">
	Add a host based route on the frontend to address 10.0.0.2 with the gateway 10.0.0.1
	through interface eth1.2. This will tag the packet with the vlan ID of 2.
	The syncnow flag being set to true will also add it to the live routing table so no network restart
	is needed.
	</example>
	"""

	def run(self, params, args):
		if len(args) == 0:
			raise ArgRequired(self, 'host')

		self.command('add.route', self._argv + ['scope=host'], verbose_errors = False)
		return self.rc

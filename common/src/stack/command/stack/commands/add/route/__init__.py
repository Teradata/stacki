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
from stack.exception import CommandError


class Command(stack.commands.add.command):
	"""
	Add a route for all hosts in the cluster
	
	<param type='string' name='address' optional='0'>
	Host or network address
	</param>
	
	<param type='string' name='gateway' optional='0'>
	Network (e.g., IP address), subnet name (e.g., 'private', 'public'), or
	a device gateway (e.g., 'eth0).
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

		(address, gateway, netmask, interface) = self.fillParams([
			('address', None, True),
			('gateway', None, True),
			('netmask', '255.255.255.255'),
			('interface', None)
			])
		# check if the user has put a subnet name in the gateway field
		subnet = self.db.select("""id from subnets where name=%s """, [gateway])
		if subnet:
			# if they have, set the gateway to '' and pull the subnet name
			# out of the returned tuple
			gateway = ''
			subnet = subnet[0][0]
		else:
			# if they haven't, set the subnet to None and leave the user
			# specified gateway in the gateway field
			subnet = None

		# check if the route already exists
		rows = self.db.select("""* from global_routes
			where Network=%s""", address)
		
		if rows:
			raise CommandError(self, 'route exists')

		#
		# if interface is being set, check if it exists first
		#
		if not interface:
			interface = None
		
		self.db.execute("""insert into global_routes
				values (%s, %s, %s, %s, %s)""",
				(address, netmask, gateway, subnet, interface))

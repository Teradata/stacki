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
from stack.commands import ScopeArgProcessor
from stack.exception import CommandError
from stack.util import blank_str_to_None


class Command(ScopeArgProcessor, stack.commands.add.command):
	"""
	Add a route for all hosts in the cluster

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
		# Get the scope and make sure the args are valid
		scope, = self.fillParams([('scope', 'global')])
		scope_mappings = self.getScopeMappings(args, scope)

		# Now validate the params
		(address, gateway, netmask, interface, syncnow) = self.fillParams([
			('address', None, True),
			('gateway', None, True),
			('netmask', '255.255.255.255'),
			('interface', None),
			('syncnow', None)
		])
		syncnow = self.str2bool(syncnow)

		# Check if the user has put a subnet name in the gateway field
		rows = self.db.select('id from subnets where name=%s', [gateway])
		if rows:
			gateway = None
			subnet_id = rows[0][0]
		else:
			subnet_id = None

		# Make sure interface is None if blank
		interface = blank_str_to_None(interface)

		for scope_mapping in scope_mappings:
			# Check that the route is unique for the scope
			if self.db.count("""
		 		(routes.id) FROM routes,scope_map
				WHERE routes.scope_map_id = scope_map.id
				AND routes.address = %s
				AND scope_map.scope = %s
				AND scope_map.appliance_id <=> %s
				AND scope_map.os_id <=> %s
				AND scope_map.environment_id <=> %s
				AND scope_map.node_id <=> %s
			""", (address, *scope_mapping)) != 0:
		 		raise CommandError(self, f'route for "{address}" already exists')

		# Everything looks good, add the new routes
		for scope_mapping in scope_mappings:
			# First add the scope mapping for the new route
			self.db.execute("""
				INSERT INTO scope_map(
					scope, appliance_id, os_id, environment_id, node_id
				)
				VALUES (%s, %s, %s, %s, %s)
			""", scope_mapping)

			# Then add the route itself
			self.db.execute("""
				INSERT INTO routes(
					scope_map_id, address, netmask, gateway,
					subnet_id, interface
				)
				VALUES (LAST_INSERT_ID(), %s, %s, %s, %s, %s)
			""", (address, netmask, gateway, subnet_id, interface))

		# Sync the routes, if requested and we are 'host' scoped
		if scope == 'host' and syncnow:
			# Need to get the node ID for ourselves
			node_id = self.db.select(
				'id from nodes where name=%s',
				self.db.getHostname()
			)[0][0]

			for scope_mapping in scope_mappings:
				if scope_mapping.node_id == node_id:
					# Add the new route
					cmd = ['route', 'add', '-host', address]

					if interface:
						cmd.append('dev')
						cmd.append(interface)

					if gateway:
						cmd.append('gw')
						cmd.append(gateway)

					self._exec(cmd)

					# Sync the routes file
					self._exec("""
						/opt/stack/bin/stack report host route localhost |
						/opt/stack/bin/stack report script |
						bash > /dev/null 2>&1
					""", shell=True)

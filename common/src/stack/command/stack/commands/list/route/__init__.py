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

from operator import itemgetter

import stack.commands
from stack.commands import ScopeArgProcessor

class Command(ScopeArgProcessor, stack.commands.list.command):
	"""
	List the global routes.

	<example cmd='list route'>
	Lists all the global routes for this cluster.
	</example>
	"""

	def run(self, params, args):
		# Get the scope and make sure the args are valid
		scope, = self.fillParams([('scope', 'global')])
		scope_mappings = self.getScopeMappings(args, scope)

		self.beginOutput()
		for scope_mapping in scope_mappings:
			if scope == 'host':
				# Get the host's info for the scope linking
				host, appliance_id, os_id, environment_id = self.db.select("""
					nodes.name, appliance, boxes.os, environment
					FROM nodes, boxes
					WHERE nodes.id = %s AND nodes.box = boxes.id
				""", (scope_mapping.node_id,))[0]

				# Get all the routes for all scopes that match the host's info
				routes = self.db.select("""
					routes.address, routes.netmask, routes.gateway,
					subnets.name, routes.interface,
					UPPER(LEFT(scope_map.scope, 1))
					FROM routes
					LEFT JOIN subnets
						ON routes.subnet_id = subnets.id
					INNER JOIN scope_map
						ON routes.scope_map_id = scope_map.id
					WHERE scope_map.scope = 'global'
					OR (scope_map.scope = 'appliance' AND scope_map.appliance_id <=> %s)
					OR (scope_map.scope = 'os' AND scope_map.os_id <=> %s)
					OR (scope_map.scope = 'environment' AND scope_map.environment_id <=> %s)
					OR (scope_map.scope = 'host' AND scope_map.node_id <=> %s)
					ORDER BY scope_map.scope DESC, routes.address, routes.id
				""", (appliance_id, os_id, environment_id, scope_mapping.node_id))

				# The routes come out of the DB with the higher value scopes
				# first. Surprisingly, there is no simple way in SQL to squash
				# these rules down by scope value. So, we do it here instead.
				seen_addresses = set()
				squashed_routes = []
				for route in routes:
					if route[0] not in seen_addresses:
						squashed_routes.append(list(route))
						seen_addresses.add(route[0])

				# If the route has a subnet, we need to look up if the host has an
				# interface linked to it, and output that interface if it does
				for route in squashed_routes:
					if route[3]:
						rows = self.db.select("""
							device FROM subnets,networks,nodes
							WHERE nodes.id = %s
							AND subnets.name = %s
							AND subnets.id = networks.subnet
							AND networks.node = nodes.id
							AND networks.device NOT LIKE 'vlan%%'
						""", (scope_mapping.node_id, route[3]))

						if rows:
							route[4] = rows[0][0]

				for route in sorted(squashed_routes, key=itemgetter(0)):
					self.addOutput(host, route)
			else:
				# All the other scopes just list their routes
				routes = self.db.select("""
					COALESCE(appliances.name, oses.name, environments.name, ''),
					routes.address, routes.netmask, routes.gateway,
					subnets.name, routes.interface
					FROM routes
					LEFT JOIN subnets
						ON routes.subnet_id = subnets.id
					INNER JOIN scope_map
						ON routes.scope_map_id = scope_map.id
					LEFT JOIN appliances
						ON scope_map.appliance_id = appliances.id
					LEFT JOIN oses
						ON scope_map.os_id = oses.id
					LEFT JOIN environments
						ON scope_map.environment_id = environments.id
					WHERE scope_map.scope = %s
					AND scope_map.appliance_id <=> %s
					AND scope_map.os_id <=> %s
					AND scope_map.environment_id <=> %s
					AND scope_map.node_id <=> %s
					ORDER BY routes.address, routes.id
				""", scope_mapping)

				for route in routes:
					self.addOutput(route[0], route[1:])

		if scope == 'host':
			self.endOutput(header=[
				'host', 'network', 'netmask', 'gateway', 'subnet',
				'interface', 'source'
			])
		elif scope == 'global':
			self.endOutput(header=[
				'', 'network', 'netmask', 'gateway', 'subnet', 'interface'
			])
		else:
			self.endOutput(header=[
				scope, 'network', 'netmask', 'gateway','subnet', 'interface'
			])

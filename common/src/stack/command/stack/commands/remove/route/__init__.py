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

class Command(ScopeArgProcessor, stack.commands.remove.command):
	"""
	Remove a global static route.

	<param type='string' name='address' optional='0'>
	The address of the static route to remove.
	</param>

	<example cmd='remove route address=1.2.3.4'>
	Remove the global static route that has the network address '1.2.3.4'.
	</example>
	"""

	def run(self, params, args):
		# Get the scope and make sure the args are valid
		scope, = self.fillParams([('scope', 'global')])
		scope_mappings = self.getScopeMappings(args, scope)

		# Now validate the params
		(address, syncnow) = self.fillParams([
			('address', None, True),
			('syncnow', None)
		])
		syncnow = self.str2bool(syncnow)

		scope_ids = []
		for scope_mapping in scope_mappings:
			# Check that the route address exists for the scope
			rows = self.db.select("""
		 		scope_map.id FROM routes,scope_map
				WHERE routes.scope_map_id = scope_map.id
				AND routes.address = %s
				AND scope_map.scope = %s
				AND scope_map.appliance_id <=> %s
				AND scope_map.os_id <=> %s
				AND scope_map.environment_id <=> %s
				AND scope_map.node_id <=> %s
			""", (address, *scope_mapping))

			if not rows:
		 		raise CommandError(
					 self, f'route with address "{address}" does not exist'
				)

			scope_ids.append(rows[0][0])

		# Routes existed for all the scope mappings, so delete them
		# Note: We just delete the scope mapping, the ON DELETE CASCADE takes
		# care of removing the routes table entries for us.
		self.db.execute('delete from scope_map where id in %s', (scope_ids,))

		# Sync the routes, if requested and we are 'host' scoped
		if scope == 'host' and syncnow:
			# Need to get the node ID for ourselves
			node_id = self.db.select(
				'id from nodes where name=%s',
				self.db.getHostname()
			)[0][0]

			for scope_mapping in scope_mappings:
				if scope_mapping.node_id == node_id:
					# Remove the route
					self._exec(f'route del -host {address}', shlexsplit=True)

					# Sync the routes file
					self._exec("""
						/opt/stack/bin/stack report host route localhost |
						/opt/stack/bin/stack report script |
						bash > /dev/null 2>&1
					""", shell=True)

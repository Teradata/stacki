# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import CommandError, ParamRequired, ParamType, ParamValue, ParamError
from stack.util import flatten


class Command(stack.commands.ScopeArgumentProcessor, stack.commands.remove.command):
	"""
	Remove a storage partition configuration from the database.

	<param type='string' name='device' optional='1'>
	Device whose partition configuration needs to be removed from
	the database.
	</param>

	<param type='string' name='mountpoint' optional='1'>
	Mountpoint for the partition that needs to be removed from
	the database.
	</param>

	<example cmd='remove storage partition device=sda'>
	Remove the global storage partition configuration for sda.
	</example>

	<example cmd='remove storage partition device=sda mountpoint=/var'>
	Remove the global storage partition configuration for /var on sda.
	</example>
	"""

	def run(self, params, args):
		# Get the scope and make sure the args are valid
		scope, = self.fillParams([('scope', 'global')])
		scope_mappings = self.getScopeMappings(args, scope)

		# Now validate the params
		device, mountpoint = self.fillParams([
			('device', None),
			('mountpoint', None)
		])

		# Global scope needs to supply either a device or mountpoint
		if scope == 'global' and not any([device, mountpoint]):
			raise ParamRequired(self, ['device', 'mountpoint'])

		scope_ids = []
		for scope_mapping in scope_mappings:
			# Check that the partition configuration exists for the scope
			query = """
				scope_map.id FROM storage_partition,scope_map
				WHERE storage_partition.scope_map_id = scope_map.id
				AND scope_map.scope = %s
				AND scope_map.appliance_id <=> %s
				AND scope_map.os_id <=> %s
				AND scope_map.environment_id <=> %s
				AND scope_map.node_id <=> %s
			"""
			values = list(scope_mapping)

			if device and device != '*':
				query += ' AND device = %s'
				values.append(device)

			if mountpoint and mountpoint != '*':
				query += ' AND mountpoint = %s'
				values.append(mountpoint)

			rows = self.db.select(query, values)
			if not rows:
				if device is None:
					device = '*'
				if mountpoint is None:
					mountpoint = '*'

				raise CommandError(self,
					f'partition specification for device "{device}" '
					f'and mount point "{mountpoint}" doesn\'t exist'
				)

			# Add the matches to the delete list
			scope_ids.extend(flatten(rows))

		# Partition  specifications existed for all the scope mappings, so delete them.
		# Note: We just delete the scope mapping, the ON DELETE CASCADE takes
		# care of removing the storage_partition table entries for us.
		self.db.execute('delete from scope_map where id in %s', (scope_ids,))

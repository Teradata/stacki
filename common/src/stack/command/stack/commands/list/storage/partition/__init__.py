# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgError, ParamValue


class Command(stack.commands.ScopeArgumentProcessor, stack.commands.list.command):
	"""
	List the global storage partition configuration.

	<example cmd='list storage partition'>
	List the global storage partition configuration for this cluster.
	</example>
	"""

	def _clean_data(self, device, partid, mountpoint, size, fstype, options, scope=None):
		if size == -1:
			size = "recommended"
		elif size == -2:
			size = "hibernation"

		if partid == 0:
			partid = None

		if scope:
			return [device, partid, mountpoint, size, fstype, options, scope]
		else:
			return [device, partid, mountpoint, size, fstype, options]

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

				# Get the controller data for all scopes that match the host's info
				rows = self.db.select("""
					storage_partition.device, storage_partition.partid,
					storage_partition.mountpoint, storage_partition.size,
					storage_partition.fstype, storage_partition.options,
					UPPER(LEFT(scope_map.scope, 1))
					FROM storage_partition
					INNER JOIN scope_map
						ON storage_partition.scope_map_id = scope_map.id
					WHERE scope_map.scope = 'global'
					OR (scope_map.scope = 'appliance' AND scope_map.appliance_id <=> %s)
					OR (scope_map.scope = 'os' AND scope_map.os_id <=> %s)
					OR (scope_map.scope = 'environment' AND scope_map.environment_id <=> %s)
					OR (scope_map.scope = 'host' AND scope_map.node_id <=> %s)
					ORDER BY scope_map.scope DESC, device, partid, size, fstype
				""", (appliance_id, os_id, environment_id, scope_mapping.node_id))

				# The routes come out of the DB with the higher value scopes
				# first. First scope wins, so we output until the scope changes.
				last_scope = None
				for row in rows:
					if last_scope and last_scope != row[6]:
						break

					self.addOutput(host, self._clean_data(*row))

					last_scope = row[6]
			else:
				# All the other scopes just list their data
				rows = self.db.select("""
					COALESCE(appliances.name, oses.name, environments.name, ''),
					storage_partition.device, storage_partition.partid,
					storage_partition.mountpoint, storage_partition.size,
					storage_partition.fstype, storage_partition.options
					FROM storage_partition
					INNER JOIN scope_map
						ON storage_partition.scope_map_id = scope_map.id
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
					ORDER BY device, partid, size, fstype
				""", scope_mapping)

				for row in rows:
					self.addOutput(row[0], self._clean_data(*row[1:]))

		if scope == 'host':
			self.endOutput(header=[
				'host', 'device', 'partid', 'mountpoint',
				'size', 'fstype', 'options', 'source'
			])
		elif scope == 'global':
			self.endOutput(header=[
				'', 'device', 'partid', 'mountpoint',
				'size', 'fstype', 'options'
			])
		else:
			self.endOutput(header=[
				scope, 'device', 'partid', 'mountpoint',
				'size', 'fstype', 'options'
			])

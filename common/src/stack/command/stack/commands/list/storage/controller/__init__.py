# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.commands import ScopeArgProcessor
from stack.exception import ArgError, ParamValue


class Command(ScopeArgProcessor, stack.commands.list.command):
	"""
	List the global storage controller configuration.

	<example cmd='list storage controller'>
	List the global storage controller configuration for this cluster.
	</example>
	"""

	def _clean_data(self, enclosure, adapter, slot, raidlevel, arrayid, options, scope=None):
		if enclosure == -1:
			enclosure = None

		if adapter == -1:
			adapter = None

		if slot == -1:
			slot = '*'

		if raidlevel == '-1':
			raidlevel = 'hotspare'

		if arrayid == -1:
			arrayid = 'global'
		elif arrayid == -2:
			arrayid = '*'

		options = options.strip('"')

		if scope:
			return [enclosure, adapter, slot, raidlevel, arrayid, options, scope]
		else:
			return [enclosure, adapter, slot, raidlevel, arrayid, options]

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
					storage_controller.enclosure, storage_controller.adapter,
					storage_controller.slot, storage_controller.raidlevel,
					storage_controller.arrayid, storage_controller.options,
					UPPER(LEFT(scope_map.scope, 1))
					FROM storage_controller
					INNER JOIN scope_map
						ON storage_controller.scope_map_id = scope_map.id
					WHERE scope_map.scope = 'global'
					OR (scope_map.scope = 'appliance' AND scope_map.appliance_id <=> %s)
					OR (scope_map.scope = 'os' AND scope_map.os_id <=> %s)
					OR (scope_map.scope = 'environment' AND scope_map.environment_id <=> %s)
					OR (scope_map.scope = 'host' AND scope_map.node_id <=> %s)
					ORDER BY scope_map.scope DESC, enclosure, adapter, slot
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
					storage_controller.enclosure, storage_controller.adapter,
					storage_controller.slot, storage_controller.raidlevel,
					storage_controller.arrayid, storage_controller.options
					FROM storage_controller
					INNER JOIN scope_map
						ON storage_controller.scope_map_id = scope_map.id
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
					ORDER BY enclosure, adapter, slot
				""", scope_mapping)

				for row in rows:
					self.addOutput(row[0], self._clean_data(*row[1:]))

		if scope == 'host':
			self.endOutput(header=[
				'host', 'enclosure', 'adapter', 'slot',
				'raidlevel', 'arrayid', 'options', 'source'
			])
		elif scope == 'global':
			self.endOutput(header=[
				'', 'enclosure', 'adapter', 'slot',
				'raidlevel', 'arrayid', 'options'
			])
		else:
			self.endOutput(header=[
				scope, 'enclosure', 'adapter', 'slot',
				'raidlevel', 'arrayid', 'options'
			])

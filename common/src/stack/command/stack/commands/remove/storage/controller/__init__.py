# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.commands import ScopeArgProcessor
from stack.exception import CommandError, ParamRequired, ParamType, ParamValue, ParamError
from stack.util import flatten


class Command(ScopeArgProcessor, stack.commands.remove.command):
	"""
	Remove a storage controller configuration from the database.

	<param type='integer' name='adapter' optional='1'>
	Adapter address. If adapter is '*', enclosure/slot address applies to
	all adapters.
	</param>

	<param type='integer' name='enclosure' optional='1'>
	Enclosure address. If enclosure is '*', adapter/slot address applies
	to all enclosures.
	</param>

	<param type='integer' name='slot' optional='0'>
	Slot address(es). This can be a comma-separated list. If slot is '*',
	adapter/enclosure address applies to all slots.
	</param>

	<example cmd='remove storage controller slot=1'>
	Remove the global disk array configuration for slot 1.
	</example>

	<example cmd='remove storage controller slot=1,2,3,4'>
	Remove the global disk array configuration for slots 1-4.
	</example>
	"""

	def run(self, params, args):
		# Get the scope and make sure the args are valid
		scope, = self.fillParams([('scope', 'global')])
		scope_mappings = self.getScopeMappings(args, scope)

		# Now validate the params
		adapter, enclosure, slot = self.fillParams([
			('adapter', None),
			('enclosure', None),
			('slot', None, True)
		])

		# Make sure the adapter is an integer greater than 0, if it exists
		if adapter and adapter != '*':
			try:
				adapter = int(adapter)
			except:
				raise ParamType(self, 'adapter', 'integer')

			if adapter < 0:
				raise ParamValue(self, 'adapter', '>= 0')
		else:
			adapter = None

		# Make sure the enclosure is an integer greater than 0, if it exists
		if enclosure and enclosure != '*':
			try:
				enclosure = int(enclosure)
			except:
				raise ParamType(self, 'enclosure', 'integer')

			if enclosure < 0:
				raise ParamValue(self, 'enclosure', '>= 0')
		else:
			enclosure = None

		# Parse the slots
		slots = []
		if slot:
			for s in slot.split(','):
				# Make sure the slot is valid
				if s == '*':
					# We're removing them all
					s = None
				else:
					try:
						s = int(s)
					except:
						raise ParamType(self, 'slot', 'integer')

					if s < 0:
						raise ParamValue(self, 'slot', '>= 0')

					if s in slots:
						raise ParamError(
							self, 'slot', f'"{s}" is listed twice'
						)

				# Looks good
				slots.append(s)

		scope_ids = []
		for scope_mapping in scope_mappings:
			for slot in slots:
				# Check that the controller configuration exists for the scope
				query = """
					scope_map.id FROM storage_controller,scope_map
					WHERE storage_controller.scope_map_id = scope_map.id
					AND scope_map.scope = %s
					AND scope_map.appliance_id <=> %s
					AND scope_map.os_id <=> %s
					AND scope_map.environment_id <=> %s
					AND scope_map.node_id <=> %s
				"""
				values = list(scope_mapping)

				# 0 might be valid so need to check for None
				if adapter is not None:
					query += " AND storage_controller.adapter = %s"
					values.append(adapter)

				if enclosure is not None:
					query += " AND storage_controller.enclosure = %s"
					values.append(enclosure)

				if slot is not None:
					query += " AND storage_controller.slot = %s"
					values.append(slot)

				rows = self.db.select(query, values)
				if not rows:
					if adapter is None:
						adapter = '*'
					if enclosure is None:
						enclosure = '*'
					if slot is None:
						slot = '*'

					raise CommandError(
						self,
						f'disk specification for "{adapter}/'
						f'{enclosure}/{slot}" doesn\'t exist'
					)

				scope_ids.extend(flatten(rows))

		# Controller disk specifications existed for all the scope mappings,
		# so delete them.
		# Note: We just delete the scope mapping, the ON DELETE CASCADE takes
		# care of removing the storage_controller table entries for us.
		self.db.execute('delete from scope_map where id in %s', (scope_ids,))

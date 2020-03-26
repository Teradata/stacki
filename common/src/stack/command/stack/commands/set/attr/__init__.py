# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import fnmatch
from functools import lru_cache
import os
import re

import stack.commands
from stack.commands import ScopeArgProcessor
from stack.exception import CommandError, ArgRequired


class Command(ScopeArgProcessor, stack.commands.set.command):
	"""
	Sets a global attribute for all nodes

	<param type='string' name='attr' optional='0'>
	Name of the attribute
	</param>

	<param type='string' name='value' optional='0'>
	Value of the attribute
	</param>

	<param type='boolean' name='shadow'>
	If set to true, then set the 'shadow' value (only readable by root
	and apache).
	</param>

	<example cmd='set attr attr=sge value=False'>
	Sets the sge attribution to False
	</example>

	<related>list attr</related>
	<related>remove attr</related>
	"""

	# Cache the expensive calls to fnmatchcase for when there are multiple targets
	@lru_cache(maxsize=None)
	def _fnmatchcase(self, name, pattern):
		return fnmatch.fnmatchcase(name, pattern)

	def run(self, params, args):
		# Get the scope and make sure the args are valid
		scope, = self.fillParams([('scope', 'global')])
		scope_mappings = self.getScopeMappings(args, scope)

		# Now validate the params
		attr, value, shadow, force = self.fillParams([
			('attr',   None, True),
			('value',  None, True),
			('shadow', False),
			('force',  True)
		])

		shadow = self.str2bool(shadow)
		force  = self.str2bool(force)

		if not scope == 'global' and not args:
			raise ArgRequired(self)

		is_glob = re.match('^[a-zA-Z_][a-zA-Z0-9_.]*$', attr) is None

		# If the value is set (we are not removing attributes) do not
		# allow the attr argument to be a glob
		if value and is_glob:
			raise CommandError(self, f'invalid attr name "{attr}"')

		# Get a list of all matching attrs in the scope, for both normal and shadow
		scope_map_ids = []
		for table in ('attributes', 'shadow.attributes'):
			query = """
				attributes.name, scope_map.id
				FROM %s, scope_map
				WHERE attributes.scope_map_id = scope_map.id
				AND scope_map.scope = %%s
			""" % table
			values = [scope]

			if scope == 'appliance':
				query += "AND scope_map.appliance_id IN %s"
				values.append([s.appliance_id for s in scope_mappings])

			if scope == 'os':
				query += "AND scope_map.os_id IN %s"
				values.append([s.os_id for s in scope_mappings])

			if scope == 'environment':
				query += "AND scope_map.environment_id IN %s"
				values.append([s.environment_id for s in scope_mappings])

			if scope == 'host':
				query += "AND scope_map.node_id IN %s"
				values.append([s.node_id for s in scope_mappings])

			# If we aren't a glob, we can let the DB filter by case-insensitive name
			if not is_glob:
				query += "AND attributes.name = %s"
				values.append(attr)

			# Filter to what matches the glob pattern. This will also take care
			# of the case-sensitive matching of the attr name.
			for name, scope_map_id in self.db.select(query, values):
				if self._fnmatchcase(name, attr):
					scope_map_ids.append(scope_map_id)

		# If we aren't forcing, we throw an error if the attr already exists in this scope
		if not force and len(scope_map_ids):
			raise CommandError(self, f'attr "{attr}" already exists')

		# We got here, so delete any existing matching attrs
		if len(scope_map_ids):
			self.db.execute('delete from scope_map where id in %s', (scope_map_ids,))

		# Calls without a value are a remove, so we're done
		if not value:
			return

		# Set the attr in the correct database for each scope_mapping
		for scope_mapping in scope_mappings:
			# First add the scope mapping
			self.db.execute("""
				INSERT INTO scope_map(
					scope, appliance_id, os_id, environment_id, node_id
				)
				VALUES (%s, %s, %s, %s, %s)
			""", scope_mapping)

			# Then add the attr entry
			if shadow:
				self.db.execute("""
					INSERT INTO shadow.attributes(scope_map_id, name, value)
					VALUES (LAST_INSERT_ID(), %s, %s)
				""", (attr, value))

			else:
				self.db.execute("""
					INSERT INTO attributes(scope_map_id, name, value)
					VALUES (LAST_INSERT_ID(), %s, %s)
				""", (attr, value))

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

from collections import defaultdict
import fnmatch
from functools import lru_cache
import os
import re

import stack.commands
from stack.commands import ScopeArgProcessor
from stack.bool import str2bool
from stack.exception import CommandError
from stack.util import flatten


class Command(ScopeArgProcessor, stack.commands.list.command):
	"""
	Lists the set of global attributes.

	<param type='string' name='attr'>
	A shell syntax glob pattern to specify to attributes to
	be listed.
	</param>

	<param type='boolean' name='shadow'>
	Specifies is shadow attributes are listed, the default
	is True.
	</param>

	<example cmd='list attr'>
	List the global attributes.
	</example>
	"""

	# Cache the expensive calls to fnmatchcase for when there are multiple targets
	@lru_cache(maxsize=None)
	def _fnmatchcase(self, name, pattern):
		return fnmatch.fnmatchcase(name, pattern)

	def _construct_host_query(self, node_ids, table, attr_type, attr, is_glob):
		joins = (
			"INNER JOIN scope_map ON scope_map.node_id = nodes.id",
			"INNER JOIN scope_map ON scope_map.environment_id = nodes.environment",
			"""
			INNER JOIN boxes ON nodes.box = boxes.id
			INNER JOIN scope_map ON scope_map.os_id = boxes.os
			""",
			"INNER JOIN scope_map ON scope_map.appliance_id = nodes.appliance",
		)

		parts = []
		values = []
		for join in joins:
			part = f"""
			(
				SELECT nodes.name, scope_map.scope, '{attr_type}', attributes.name, attributes.value
				FROM nodes
				{join}
				INNER JOIN {table} ON attributes.scope_map_id = scope_map.id
				WHERE nodes.id IN %s
			"""
			values.append(node_ids)

			# If we aren't a glob, we can let the DB filter by case-insensitive name
			if attr and not is_glob:
				part += "AND attributes.name = %s "
				values.append(attr)

			part += ")"
			parts.append(part)

		query = " UNION ".join(parts)

		return query, values

	def run(self, params, args):
		# Get the scope and make sure the args are valid
		scope, = self.fillParams([('scope', 'global')])
		scope_mappings = self.getScopeMappings(args, scope)

		# Now validate the params
		attr, shadow, resolve, var, const, display = self.fillParams([
			('attr',   None),
			('shadow', True),
			('resolve', True),
			('var', True),
			('const', True),
			('display', 'all'),
		])

		# If there isn't any environments, scope_mappings could be
		# an empty list, in which case we are done
		if not scope_mappings:
			return

		# Make sure bool params are bools
		resolve = self.str2bool(resolve)
		shadow = self.str2bool(shadow)
		var = self.str2bool(var)
		const = self.str2bool(const)

		is_glob = attr is not None and re.match('^[a-zA-Z_][a-zA-Z0-9_.]*$', attr) is None

		output = defaultdict(dict)
		if var:
			if resolve and scope == 'host':
				node_ids = [s.node_id for s in scope_mappings]

				hostnames = flatten(self.db.select(
					"nodes.name FROM nodes WHERE nodes.id IN %s",
					[node_ids]
				))

				# Get all the normal attributes for the host's scopes
				query, values = self._construct_host_query(
					node_ids, 'attributes', 'var', attr, is_glob
				)

				# The attributes come out of the DB with the higher weighted
				# scopes first. Surprisingly, there is no simple way in SQL
				# to squash these rules down by scope weight. So, we do it
				# here instead. Also, filter by attr name, if provided.
				seen = defaultdict(set)
				for host, *row in self.db.select(query, values, prepend_select=False):
					if row[2] not in seen[host]:
						if attr is None or self._fnmatchcase(row[2], attr):
							output[host][row[2]] = row
						seen[host].add(row[2])

				# Merge in any normal global attrs for each host
				query = """
					'global', 'var', attributes.name, attributes.value
					FROM attributes, scope_map
					WHERE attributes.scope_map_id = scope_map.id
					AND scope_map.scope = 'global'
				"""
				values = []

				# If we aren't a glob, we can let the DB filter by case-insensitive name
				if attr and not is_glob:
					query += "AND attributes.name = %s"
					values.append(attr)

				for row in self.db.select(query, values):
					for host in hostnames:
						if row[2] not in seen[host]:
							if attr is None or self._fnmatchcase(row[2], attr):
								output[host][row[2]] = row
							seen[host].add(row[2])

				# Now get the shadow attributes, if requested
				if shadow:
					query, values = self._construct_host_query(
						node_ids, 'shadow.attributes', 'shadow', attr, is_glob
					)

					# Merge in the shadow attributes for the host's scopes
					weights = {
						'global': 0,
						'appliance': 1,
						'os': 2,
						'environment': 3,
						'host': 4
					}

					for host, *row in self.db.select(query, values, prepend_select=False):
						if row[2] not in seen[host]:
							# If we haven't seen it
							if attr is None or self._fnmatchcase(row[2], attr):
								output[host][row[2]] = row
							seen[host].add(row[2])
						else:
							# Maybe the shadow attr is higher scope
							if weights[row[0]] >= weights[output[host][row[2]][0]]:
								output[host][row[2]] = row

					# Merge in any shadow global attrs for each host
					query = """
						'global', 'shadow', attributes.name, attributes.value
						FROM shadow.attributes, scope_map
						WHERE attributes.scope_map_id = scope_map.id
						AND scope_map.scope = 'global'
					"""
					values = []

					# If we aren't a glob, we can let the DB filter by case-insensitive name
					if attr and not is_glob:
						query += "AND attributes.name = %s"
						values.append(attr)

					for row in self.db.select(query, values):
						for host in hostnames:
							if row[2] not in seen[host]:
								if attr is None or self._fnmatchcase(row[2], attr):
									output[host][row[2]] = row
								seen[host].add(row[2])
							else:
								if output[host][row[2]][0] == 'global':
									output[host][row[2]] = row

			else:
				query_data = [('attributes', 'var')]
				if shadow:
					query_data.append(('shadow.attributes', 'shadow'))

				for table, attr_type in query_data:
					if scope == 'global':
						query = f"""
							'', 'global', '{attr_type}', attributes.name, attributes.value
							FROM {table}
							INNER JOIN scope_map ON attributes.scope_map_id = scope_map.id
							WHERE scope_map.scope = 'global'
						"""
					else:
						query = f"""
							target.name, scope_map.scope, '{attr_type}', attributes.name, attributes.value
							FROM {table}
							INNER JOIN scope_map ON attributes.scope_map_id = scope_map.id
						"""
					values = []


					if scope == 'appliance':
						query += """
							INNER JOIN appliances AS target ON target.id = scope_map.appliance_id
							WHERE scope_map.appliance_id IN %s
						"""
						values.append([s.appliance_id for s in scope_mappings])

					elif scope == 'os':
						query += """
							INNER JOIN oses AS target ON target.id = scope_map.os_id
							WHERE scope_map.os_id IN %s
						"""
						values.append([s.os_id for s in scope_mappings])

					elif scope == 'environment':
						query += """
							INNER JOIN environments AS target ON target.id = scope_map.environment_id
							WHERE scope_map.environment_id IN %s
						"""
						values.append([s.environment_id for s in scope_mappings])

					elif scope == 'host':
						query += """
							INNER JOIN nodes AS target ON target.id = scope_map.node_id
							WHERE scope_map.node_id IN %s
						"""
						values.append([s.node_id for s in scope_mappings])

					# If we aren't a glob, we can let the DB filter by case-insensitive name
					if attr and not is_glob:
						query += "AND attributes.name = %s"
						values.append(attr)

					# Filter by attr name, if provided.
					for target, *row in self.db.select(query, values):
						if attr is None or self._fnmatchcase(row[2], attr):
							output[target][row[2]] = row

		if const:
			# For any host targets, figure out if they have a "const_overwrite" attr
			node_ids = [s.node_id for s in scope_mappings if s.scope == 'host']

			const_overwrite = defaultdict(lambda: True)
			if node_ids:
				for target, value in self.db.select("""
					nodes.name, attributes.value
					FROM attributes
					INNER JOIN scope_map ON attributes.scope_map_id = scope_map.id
					INNER JOIN nodes ON scope_map.node_id = nodes.id
					WHERE attributes.name = BINARY 'const_overwrite'
					AND scope_map.scope = 'host'
					AND scope_map.node_id IN %s
				""", (node_ids,)):
					const_overwrite[target] = self.str2bool(value)

			# Now run the plugins and merge in the intrensic attrs
			results = self.runPlugins(scope_mappings)
			for result in results:
				for target, *row in result[1]:
					if attr is None or self._fnmatchcase(row[2], attr):
						if const_overwrite[target]:
							output[target][row[2]] = row
						else:
							if row[2] not in output[target]:
								output[target][row[2]] = row

		# Handle the display parameter if we are host scoped
		self.beginOutput()
		if scope == 'host' and display in {'common', 'distinct'}:
			# Construct a set of attr (name, value) for each target
			host_attrs = {}
			for target in output:
				host_attrs[target] = {
					(row[2], str(row[3])) for row in output[target].values()
				}

			common_attrs = set.intersection(*host_attrs.values())

			if display == 'common':
				for name, value in sorted(common_attrs):
					self.addOutput('_common_', [None, None, name, value])

			elif display == 'distinct':
				common_attr_names = set(v[0] for v in common_attrs)

				for target in sorted(output.keys()):
					for key in sorted(output[target].keys()):
						if key not in common_attr_names:
							self.addOutput(target, output[target][key])
		else:
			# Output our combined attributes, sorting them by target then attr
			for target in sorted(output.keys()):
				for key in sorted(output[target].keys()):
					self.addOutput(target, output[target][key])

		if scope == 'global':
			header = ''
		else:
			header = scope

		self.endOutput(header=[
			header, 'scope', 'type', 'attr', 'value'
		])

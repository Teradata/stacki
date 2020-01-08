from collections import defaultdict
import fnmatch
from functools import lru_cache
import os
import re

from pymysql import OperationalError

from stack.bool import str2bool
from stack.graphql.resolvers import error, mutation, query, success
from stack.graphql.resolvers.plugins import registry
from stack.graphql.scope import create_scope_query, resolve_scope_targets, create_scope_map_insert_queries
from stack.graphql.utils import create_common_filters, map_kwargs


# Cache the expensive calls to fnmatchcase for when there are multiple targets
@lru_cache(maxsize=1024)
def _fnmatchcase(name, pattern):
	return fnmatch.fnmatchcase(name, pattern)

@query.field("attributes")
@map_kwargs({"id": "id_"})
def attributes(
	obj, info, id_=None, name=None, resolve=True, var=True, const=True,
	shadow=True, scope="global", targets=None
):
	results = defaultdict(dict)

	def _is_higher_scope(row):
		weights = {
			'global': 0,
			'appliance': 1,
			'os': 2,
			'environment': 3,
			'host': 4
		}

		existing = results[row["target"]][row["name"]]
		return weights[row["scope"]] >= weights[existing["scope"]]

	def _add_results(rows, overwrite=False, shadow=False):
		for row in rows:
			if not name or _fnmatchcase(row["name"], name):
				existing = row["name"] in results[row["target"]]

				if not existing or overwrite or (shadow and _is_higher_scope(row)):
					results[row["target"]][row["name"]] = row

	# Resolve our targets. If nothing is returned then we are done.
	resolved_targets = resolve_scope_targets(info.context, scope, targets)
	if not resolved_targets:
		return []

	# Get the database attributes, if requested
	if var:
		# First get the normal attributes
		query, values = create_scope_query(scope, "attributes", [
			"attributes.id", "'var' AS type", "attributes.name", "value"
		], id_, resolved_targets, resolve)

		info.context.execute(query, values)
		_add_results(info.context.fetchall())

		# If we are host scoped and resolving, we need to pull in the global attrs too
		if scope == "host" and resolve:
			query, values = create_scope_query("global", "attributes", [
				"attributes.id", "'var' AS type", "attributes.name", "value"
			], id_)

			info.context.execute(query, values)

			# We have to construct a row for each hostname
			rows = []
			for row in info.context.fetchall():
				for hostname in resolved_targets:
					clone = row.copy()
					clone["target"] = hostname
					rows.append(clone)
			_add_results(rows)

		# Then get the shadow attributes, if requested
		if shadow:
			query, values = create_scope_query(scope, "shadow.attributes", [
				"attributes.id", "'shadow' AS type", "attributes.name", "value"
			], id_, resolved_targets, resolve)

			try:
				info.context.execute(query, values)
				_add_results(info.context.fetchall(), shadow=True)
			except OperationalError:
				# User didn't have permission to the shadow db
				pass

			# If we are host scoped and resolving, we also need the shadow global attrs
			if scope == "host" and resolve:
				query, values = create_scope_query("global", "shadow.attributes", [
					"attributes.id", "'shadow' AS type", "attributes.name", "value"
				], id_)

				try:
					info.context.execute(query, values)

					# We have to construct a row for each hostname
					rows = []
					for row in info.context.fetchall():
						for hostname in resolved_targets:
							clone = row.copy()
							clone["target"] = hostname
							rows.append(clone)
					_add_results(rows, shadow=True)
				except OperationalError:
					# User didn't have permission to the shadow db
					pass

	# Pull in constant attributes, if requested
	if const:
		const_overwrite = defaultdict(lambda: True)

		if scope == "host":
			# For host targets, figure out if they have a "const_overwrite" attribute,
			# which can be set to False to prevent constants from overwriting host attributes
			info.context.execute("""
				SELECT nodes.name, attributes.value
				FROM attributes
				INNER JOIN scope_map ON attributes.scope_map_id = scope_map.id
				INNER JOIN nodes ON scope_map.node_id = nodes.id
				WHERE attributes.name = BINARY 'const_overwrite'
				AND scope_map.scope = 'host'
				AND nodes.name IN %s
			""", (resolved_targets,))

			for row in info.context.fetchall():
				const_overwrite[row["name"]] = str2bool(row["value"])

		for result in registry.run_plugins("attributes", info.context, scope, resolved_targets):
			for target in result:
				_add_results(result[target].values(), overwrite=const_overwrite[target])

	# Sort the output by target then name
	output = []
	for target in sorted(results.keys()):
		for name in sorted(results[target].keys()):
			output.append(results[target][name])

	return output

@query.field("attributes_exist")
def attributes_exist(obj, info, names=None, scope="global", targets=None):
	lookups = []

	if names:
		# Gather up the lookup results
		for name in names:
			results = attributes(
				obj, info, name=name, resolve=False, const=False,
				scope=scope, targets=targets
			)

			lookups.append({
				"name": name,
				"exists": len(results) != 0
			})

	return lookups

@mutation.field("add_attribute")
def add_attribute(obj, info, name, value, shadow=False, force=False, scope="global", targets=None):
	# Validate the name
	if re.match('^[a-zA-Z_][a-zA-Z0-9_.]*$', name) is None:
		return error(f'invalid attr name "{name}"')

	# If we aren't forcing, make sure the attribute doesn't already exist
	if not force:
		results = attributes(
			obj, info, name=name, resolve=False, const=False,
			scope=scope, targets=targets
		)

		if len(results):
			return error(f'attr "{name}" already exists')
	else:
		# We are force adding, so make sure any existing attributes are gone
		remove_attribute(obj, info, name=name, scope=scope, targets=targets)

	# Create the scope_map entries and attributes
	for query, values in create_scope_map_insert_queries(info.context, scope, targets):
		# Create the scope map entry
		info.context.execute(query, values)

		# Now insert the new attribute
		table = "shadow.attributes" if shadow else "attributes"

		info.context.execute(f"""
			INSERT INTO {table}(scope_map_id, name, value)
			VALUES (LAST_INSERT_ID(), %s, %s)
		""", (name, value))

	# Now return our new data
	return success(attributes=attributes(
		obj, info, name=name, resolve=False, const=False, shadow=shadow,
		scope=scope, targets=targets
	))

@mutation.field("remove_attribute")
@map_kwargs({"id": "id_"})
def remove_attribute(obj, info, id_=None, name=None, scope="global", targets=None):
	# Not being given a remove target is a no-op
	if id_ or name:
		# Get a list of matching attributes
		results = attributes(
			obj, info, id_=id_, name=name, resolve=False, const=False,
			scope=scope, targets=targets
		)

		# Split the results into normal and shadow lists
		normal_ids = []
		shadow_ids = []
		for attribute in results:
			if attribute["type"] == "shadow":
				shadow_ids.append(attribute["id"])
			else:
				normal_ids.append(attribute["id"])

		# Delete the normal attributes
		# Note: This will cascade delete the attribute data
		if normal_ids:
			info.context.execute("""
				DELETE FROM scope_map
				WHERE id IN (
					SELECT scope_map_id
					FROM attributes
					WHERE attributes.id IN %s
				)
			""", (normal_ids,))

		# And the shadow ones
		# Note: Again, cascade delete is our friend
		if shadow_ids:
			info.context.execute("""
				DELETE FROM scope_map
				WHERE id IN (
					SELECT scope_map_id
					FROM shadow.attributes
					WHERE attributes.id IN %s
				)
			""", (shadow_ids,))

	return success()

from stack.graphql.utils import create_common_filters


def resolve_scope_targets(cursor, scope, targets):
	"""
	Returns a list of names for scopes that match the target patterns.
	"""

	names = []
	if scope == "global":
		names.append("global")
	else:
		scope_to_table = {
			"appliance": "appliances",
			"os": "oses",
			"environment": "environments",
			"host": "nodes"
		}

		query = f"SELECT name FROM {scope_to_table[scope]}"
		filters, values = create_common_filters(None, targets)

		if filters:
			query += " WHERE " + " AND ".join(filters)

		query += " ORDER BY name"

		cursor.execute(query, values)
		for row in cursor.fetchall():
			names.append(row["name"])

	return names

def create_scope_query(scope, table, fields, id_filter=None, targets=None, resolve=False):
	"""
	Returns a query wired up to resolve the scopes, and a list of values to
	pass to the execute function.
	"""

	values = []

	if scope == "global":
		query = f"""
			SELECT 'global' AS target, scope, {', '.join(fields)}
			FROM {table}
			INNER JOIN scope_map ON scope_map.id = attributes.scope_map_id
		"""

		filters, filter_values = create_common_filters(id_filter, None, f"{table}.id")
		if filters:
			values.extend(filter_values)

		filters.append("scope_map.scope = 'global'")

		query += " WHERE " + " AND ".join(filters)
		query += f" ORDER BY {table}.name"

	elif scope == "host" and resolve:
		# We're going to be constructing a UNION ALL query with a part for every
		# scope that is attached to a given host
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
			query = f"""
				SELECT nodes.name AS target, scope, {', '.join(fields)}
				FROM nodes
				{join}
				INNER JOIN {table} ON {table}.scope_map_id = scope_map.id
			"""

			filters, filter_values = create_common_filters(
				id_filter, targets, f"{table}.id", "nodes.name"
			)

			if filters:
				query += " WHERE " + " AND ".join(filters)
				values.extend(filter_values)

			query += f" ORDER BY target, {table}.name"

			parts.append(query)

		query = "(\n" + "\n) UNION ALL (\n".join(parts) + "\n)"
	else:
		scope_table, scope_fk = {
			"global": (None, None),
			"appliance": ("appliances", "appliance_id"),
			"os": ("oses", "os_id"),
			"environment": ("environments", "environment_id"),
			"host": ("nodes", "node_id")
		}[scope]

		query = f"""
			SELECT {scope_table}.name AS target, scope, {', '.join(fields)}
			FROM {table}
			INNER JOIN scope_map ON scope_map.id = {table}.scope_map_id
			INNER JOIN {scope_table} ON {scope_table}.id = scope_map.{scope_fk}
		"""

		filters, filter_values = create_common_filters(
			id_filter, targets, f"{table}.id", f"{scope_table}.name"
		)

		if filters:
			query += " WHERE " + " AND ".join(filters)
			values.extend(filter_values)

		query += f" ORDER BY target, {table}.name"

	return query, values

def create_scope_map_insert_queries(cursor, scope, targets=None):
	"""
	Returns a list of queries to insert new scope_map entries for the
	provided scope and targets
	"""

	def _get_target_ids(table):
		query = f"SELECT id FROM {table}"
		filters, values = create_common_filters(None, targets)

		if filters:
			query += " WHERE " + " AND ".join(filters)

		query += " ORDER BY id"

		cursor.execute(query, values)
		return [row["id"] for row in cursor.fetchall()]

	values = []

	# Get the values for the queries
	if scope == "global":
		values.append((scope, None, None, None, None))

	elif scope == "appliance":
		for appliance_id in _get_target_ids("appliances"):
			values.append((scope, appliance_id, None, None, None))

	elif scope == "os":
		for os_id in _get_target_ids("oses"):
			values.append((scope, None, os_id, None, None))

	elif scope == "environment":
		for environment_id in _get_target_ids("environments"):
			values.append((scope, None, None, environment_id, None))

	elif scope == "host":
		for node_id in _get_target_ids("nodes"):
			values.append((scope, None, None, None, node_id))

	# Each value will need an insert query
	queries = ["""
		INSERT INTO scope_map(scope, appliance_id, os_id, environment_id, node_id)
		VALUES (%s, %s, %s, %s, %s)
	"""] * len(values)

	return zip(queries, values)

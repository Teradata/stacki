# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


from ariadne import ObjectType, QueryType, MutationType
import app.db as db

query = QueryType()
mutation = MutationType()
attribute = ObjectType("Attribute")

@query.field("scope_maps")
def resolve_scope_map(parent, info, **kwargs):
	where_conditionals = {
		key: value
		for key, value in kwargs.items()
		if key in ("id", "scope", "appliance_id", "os_id", "environment_id", "node_id")
	}
	ignored_kwargs = set(where_conditionals).difference(set(kwargs))
	if ignored_kwargs:
		raise ValueError(f"Received unsupported kwargs {ignored_kwargs}")

	cmd = """
		SELECT id, scope, appliance_id, os_id, environment_id, node_id
		FROM scope_map
		{where}
	"""
	where_string = "WHERE"
	args = []
	first = True
	for key, value in kwargs.items():
		where_string += f" {'' if first else 'and '}{key}=%s"
		args.append(value)
		first = False

	if not args:
		where_string = ""

	cmd = cmd.format(where=where_string)
	result, _ = db.run_sql(cmd, args)

	return result

@attribute.field("scope_map")
def resolve_scope_map_from_parent(parent, info):
	if parent is None or not parent.get("scope_map_id"):
		return None

	cmd = """
		SELECT id, scope, appliance_id, os_id, environment_id, node_id
		FROM scope_map
		WHERE id=%s
	"""
	args = [parent.get("scope_map_id")]
	result, _ = db.run_sql(cmd, args, fetchone=True)

	return result

object_types = [attribute]

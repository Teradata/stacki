# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


from ariadne import ObjectType, QueryType, MutationType
import app.db as db

query = QueryType()
mutation = MutationType()

@query.field("attributes")
def resolve_attributes(parent, info, scope=None, scope_name=None, **kwargs):
	where_conditionals = {
		f"attributes.{key}": value
		for key, value in kwargs.items()
		if key in ("id", "scope_map_id", "name", "value")
	}
	ignored_kwargs = set(key.split(".")[-1] for key in where_conditionals.keys()).difference(set(kwargs))
	if ignored_kwargs:
		raise ValueError(f"Received unsupported kwargs {ignored_kwargs}")

	cmd = """
		SELECT attributes.id, attributes.scope_map_id, attributes.name, attributes.value
		FROM attributes
		{join}
		{where}
	"""
	join_string = ""
	if scope_name and not scope:
		raise ValueError("Cannot specify scope_name without scope")

	if scope_name and scope == "global":
		raise ValueError("Cannot specify scope_name at global scope")

	valid_scopes = ('global','appliance','os','environment', 'host')
	if scope:
		if scope not in valid_scopes:
			raise ValueError(f"{scope} is not one of the valid scopes {valid_scopes}")

		join_string = "INNER JOIN scope_map ON attributes.scope_map_id=scope_map.id "
		where_conditionals["scope_map.scope"] = scope

	if scope_name:
		if scope == 'appliance':
			table_name = "appliances"
		elif scope == 'os':
			table_name = "oses"
		elif scope == 'environment':
			table_name = "environments"
		elif scope == 'host':
			table_name = "nodes"
		else:
			raise RuntimeError(f"Bad scope {scope}")

		join_string += f"INNER JOIN {table_name} on scope_map.{scope if scope != 'host' else 'node'}_id={table_name}.id"
		where_conditionals[f"{table_name}.name"] = scope_name

	where_string = "WHERE"
	args = []
	first = True
	for key, value in where_conditionals.items():
		where_string += f" {'' if first else 'and '}{key}=%s"
		args.append(value)
		first = False

	if not args:
		where_string = ""

	cmd = cmd.format(join=join_string, where=where_string)
	result, _ = db.run_sql(cmd, args)

	return result

object_types = []

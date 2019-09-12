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


@query.field("scopeMaps")
def resolve_scope_map(parent, info, **kwargs):
    where_conditionals = {
        key: value
        for key, value in kwargs.items()
        if key in ("id", "scope", "appliance_id", "osId", "environmentId", "nodeId")
    }
    ignored_kwargs = set(where_conditionals).difference(set(kwargs))
    if ignored_kwargs:
        raise ValueError(f"Received unsupported kwargs {ignored_kwargs}")

    cmd = """
		SELECT id, scope, appliance_id as applianceId,
        os_id as osId, environment_id as environmentId, node_id as nodeId
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


@attribute.field("scopeMap")
def resolve_scope_map_from_parent(parent, info):
    if parent is None or not parent.get("scopeMapId"):
        return None

    cmd = """
		SELECT id, scope, appliance_id as applianceId,
        os_id as osId, environment_id as environmentId, node_id as nodeId
		FROM scope_map
		WHERE id=%s
	"""
    args = [parent.get("scopeMapId")]
    result, _ = db.run_sql(cmd, args, fetchone=True)

    return result


object_types = [attribute]

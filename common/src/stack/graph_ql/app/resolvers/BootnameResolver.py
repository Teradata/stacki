# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


from ariadne import ObjectType, QueryType, MutationType
import app.db as db

query = QueryType()
mutation = MutationType()
bootaction = ObjectType("Bootaction")

@query.field("bootnames")
def resolve_bootnames(*_):
    results, _ = db.run_sql("SELECT id, name, type FROM bootnames")
    return results

@bootaction.field("boot_name")
def resolve_bootname_from_parent(parent, info):
	if parent is None or not parent.get("boot_name_id"):
		return None

	cmd = """
		SELECT id, name, type
		FROM bootnames
		WHERE id=%s
	"""
	args = [parent["boot_name_id"]]
	result, _ = db.run_sql(cmd, args, fetchone=True)

	return result

object_types = [bootaction]

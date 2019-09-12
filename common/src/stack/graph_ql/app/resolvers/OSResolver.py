# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


from ariadne import ObjectType, QueryType, MutationType
import app.db as db

query = QueryType()
mutation = MutationType()
box = ObjectType("Box")
bootaction = ObjectType("Bootaction")


@query.field("oses")
def resolve_oses(*_):
    results, _ = db.run_sql("SELECT id, name FROM oses")
    return results


@bootaction.field("os")
@box.field("os")
def resolve_os_from_parent(parent, info):
    if parent is None or not parent.get("osId"):
        return None

    cmd = "SELECT id, name FROM oses WHERE id=%s"
    args = [parent["osId"]]
    result, _ = db.run_sql(cmd, args, fetchone=True)
    return result


object_types = [box, bootaction]

# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


from ariadne import ObjectType, QueryType, MutationType
import app.db as db

query = QueryType()
mutations = MutationType()
box = ObjectType("Box")


@query.field("oses")
def resolve_oses(*_):
    results, _ = db.run_sql("SELECT id, name FROM oses")
    return results


@box.field("os")
def resolve_os_from_id(box, *_):
    cmd = "SELECT id, name FROM oses WHERE id=%s"
    args = (box.get("os_id"),)
    result, _ = db.run_sql(cmd, args, fetchone=True)
    return result

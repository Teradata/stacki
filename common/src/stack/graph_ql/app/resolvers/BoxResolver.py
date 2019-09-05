# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from ariadne import ObjectType, QueryType, MutationType


import app.db as db
from app.resolvers.OSResolver import resolve_oses

query = QueryType()
mutations = MutationType()


@query.field("boxes")
def resolve_boxes(*_):
    results, _ = db.run_sql("SELECT id, name, os AS os_id FROM boxes")
    return results


@mutations.field("addBox")
def resolve_add_box(_, info, name, os="sles"):
    # TODO: get default os FROM frontend's os

    if name in [box["name"] for box in resolve_boxes()]:
        raise Exception(f"box {name} exists")

    for os_record in resolve_oses():
        if os == os_record.get("name"):
            os_id = os_record.get("id")
            break
    else:
        raise Exception(f"{os} not found in oses")

    # Insert box
    cmd = "INSERT INTO boxes (name, os) VALUES (%s, %s)"
    args = (name, os_id)
    results, _ = db.run_sql(cmd, args)

    # Get the recently inserted value
    cmd = "SELECT id, name, os AS os_id FROM boxes WHERE name=%s"
    args = (name,)
    results, _ = db.run_sql(cmd, args, fetchone=True)
    return results


@mutations.field("deleteBox")
def resolve_delete_box(_, info, id):

    cmd = "DELETE FROM boxes WHERE id=%s"
    args = (id,)
    _, affected_rows = db.run_sql(cmd, args)

    if not affected_rows:
        return False

    return True


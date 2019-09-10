# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


from ariadne import ObjectType, QueryType, MutationType
import app.db as db


query = QueryType()
mutation = MutationType()


@query.field("stacks")
def resolve_stacks(_, info, boxId=None, palletId=None):
    args = []
    params = []
    if boxId:
        params.append(" AND box = %s ")
        args.append(boxId)
    if palletId:
        params.append(" AND roll = %s ")
        args.append(palletId)
    cmd = f"SELECT box as box_id, roll as pallet_id FROM stacks WHERE 1 = 1 {''.join(params)}"
    results, _ = db.run_sql(cmd, args)
    return results


@mutation.field("addStack")
def resolve_add_stack(obj, info, boxId, palletId):
    stack = resolve_stacks(obj, info, boxId, palletId)
    if stack:
        raise Exception("The stack already exists")

    # Insert stack
    cmd = "INSERT INTO stacks (box, roll) values (%s, %s)"
    args = (boxId, palletId)
    _, affected_rows = db.run_sql(cmd, args)

    # Get the recently inserted value
    if affected_rows:
        return True

    return False


@mutation.field("deleteStack")
def resolve_delete_stack(_, info, boxId, palletId):
    # Delete stack
    cmd = "DELETE FROM stacks WHERE box=%s AND roll=%s"
    args = (boxId, palletId)
    _, affected_rows = db.run_sql(cmd, args)

    if affected_rows:
        return True

    return False


object_types = []

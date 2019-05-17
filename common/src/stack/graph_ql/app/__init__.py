# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from ariadne import (
    ObjectType,
    QueryType,
    MutationType,
    SubscriptionType,
    gql,
    make_executable_schema,
    load_schema_from_path,
)
from ariadne.asgi import GraphQL
import asyncio
import requests

from . import db

type_defs = load_schema_from_path("./app/schema/")


# TODO: Break this out into modules
query = QueryType()
mutations = MutationType()
box = ObjectType("Box")

query_fields = [query]
mutation_fields = [mutations]
object_fields = [box]


@query.field("boxes")
def resolve_boxes(*_):
    results, _ = db.run_sql("SELECT id, name, os AS os_id FROM boxes")
    return results


@query.field("oses")
def resolve_oses(*_):
    results, _ = db.run_sql("SELECT id, name FROM oses")
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


@box.field("os")
def resolve_os_from_id(box, *_):
    cmd = "SELECT id, name FROM oses WHERE id=%s"
    args = (box.get("os_id"),)
    result, _ = db.run_sql(cmd, args, fetchone=True)
    return result


@query.field("appliances")
def resolve_appliances(*_):
    results, _ = db.run_sql("SELECT id, name, public FROM appliances")
    return results


@mutations.field("addAppliance")
def resolve_add_appliance(_, info, name, public="no"):
    # TODO: Maybe make the appliance names unique in the db
    # TODO: Add kickstartable and managed attrs

    cmd = "INSERT INTO appliances (name, public) VALUES (%s, %s)"
    args = (name, public)
    db.run_sql(cmd, args)

    cmd = "SELECT id, name, public FROM appliances WHERE name=%s"
    args = (name,)
    result, _ = db.run_sql(cmd, args, fetchone=True)

    return result


@mutations.field("updateAppliance")
def resolve_update_appliance(_, info, id, name=None, public=None):
    # TODO: Maybe make the appliance names unique in the db
    # TODO: Check if the name collides

    cmd = "SELECT id, name, public FROM appliances WHERE id=%s"
    args = (id,)
    appliance, _ = db.run_sql(cmd, args, fetchone=True)
    if not appliance:
        raise Exception("No appliance found")

    if not name and not public:
        return appliance

    update_params = []
    args = ()
    if name:
        update_params.append('name="%s"')
        args += (name,)

    if public is not None:
        update_params.append('public="%s"')
        args += (public,)

    cmd = f'UPDATE appliances SET {",".join(update_params)}' + " WHERE id=%s"
    db.run_sql(cmd)

    cmd = "SELECT id, name, public FROM appliances WHERE id=%s"
    args = (id,)
    result, _ = db.run_sql(cmd, fetchone=True)

    return result


@mutations.field("deleteAppliance")
def resolve_delete_appliance(_, info, id):

    cmd = "DELETE FROM appliances WHERE id=%s"
    args = (id,)
    _, affected_rows = db.run_sql(cmd, args)

    if not affected_rows:
        return False

    return True


schema = make_executable_schema(
    type_defs, query_fields + mutation_fields + object_fields
)

# Create an ASGI app using the schema, running in debug mode
app = GraphQL(schema)


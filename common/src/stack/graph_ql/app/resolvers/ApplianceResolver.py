# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


from ariadne import ObjectType, QueryType, MutationType
import app.db as db

query = QueryType()
mutation = MutationType()
scope_map = ObjectType("ScopeMap")

@query.field("appliances")
def resolve_appliances(*_):
    results, _ = db.run_sql("SELECT id, name, public FROM appliances")
    return results

@scope_map.field("appliance")
def resolve_from_parent_id(parent, info):
	if parent is None or not parent.get("appliance_id"):
		return None

	cmd = """
		SELECT id, name, public
		FROM appliances
		WHERE id=%s
	"""
	args = [parent["appliance_id"]]
	result, _ = db.run_sql(cmd, args, fetchone=True)

	return result


@mutation.field("addAppliance")
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


@mutation.field("updateAppliance")
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
        update_params.append("name=%s")
        args += (name,)

    if public is not None:
        update_params.append("public=%s")
        args += (public,)

    args += (id,)
    cmd = f'UPDATE appliances SET {", ".join(update_params)}' + " WHERE id=%s"
    db.run_sql(cmd, args)

    cmd = "SELECT id, name, public FROM appliances WHERE id=%s"
    args = (id,)
    result, _ = db.run_sql(cmd, args, fetchone=True)

    return result


@mutation.field("deleteAppliance")
def resolve_delete_appliance(_, info, id):

    cmd = "DELETE FROM appliances WHERE id=%s"
    args = (id,)
    _, affected_rows = db.run_sql(cmd, args)

    if not affected_rows:
        return False

    return True

object_types = [scope_map]

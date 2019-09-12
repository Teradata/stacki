# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


from ariadne import ObjectType, QueryType, MutationType
import app.db as db

query = QueryType()
mutation = MutationType()


@query.field("environments")
def resolve_environments(*_):
    results, _ = db.run_sql("SELECT id, name FROM environments")

    return results


@mutation.field("addEnvironment")
def resolve_add_environment(_, info, name):

    # use resolve_environments to check if the new env name already exists
    if name in [environment["name"] for environment in resolve_environments()]:
        raise Exception(f"environment {name} exists")

    cmd = "INSERT INTO environments (name) VALUES (%s)"
    args = (name,)
    db.run_sql(cmd, args)

    cmd = "SELECT id, name FROM environments WHERE name=%s"
    args = name
    result, _ = db.run_sql(cmd, args, fetchone=True)

    return result


@mutation.field("updateEnvironment")
def resolve_update_environment(_, info, environmentId, name=None):

    cmd = "SELECT id, name FROM environments WHERE id=%s"
    args = [environmentId]
    environment, _ = db.run_sql(cmd, args, fetchone=True)
    if not environment:
        raise Exception(f"No environment found with id {environmentId}")

    # if the mutation does not specify anything to update, simply return the env
    if not name:
        return environment

    # if the mutation is updating the name with the current name, don't bother running the sql command
    if environment["name"] == name:
        return environment

    # if the updated env name is already taken, alert the user
    if name in [env["name"] for env in resolve_environments()]:
        raise Exception(f"environment {name} exists")

    update_params = []
    args = ()
    if name:
        update_params.append("name=%s")
        args += (name,)
    args += (environmentId,)
    cmd = f'UPDATE environments SET {",".join(update_params)}' + " WHERE id=%s"
    db.run_sql(cmd, args)

    args = (environmentId,)
    cmd = "SELECT id, name FROM environments WHERE id=%s"

    result, _ = db.run_sql(cmd, args, fetchone=True)

    return result


@mutation.field("deleteEnvironment")
def resolve_delete_environment(_, info, environmentId):

    cmd = "DELETE FROM environments WHERE id=%s"
    args = (environmentId,)
    _, affected_rows = db.run_sql(cmd, args)

    if not affected_rows:
        return False

    return True


object_types = []

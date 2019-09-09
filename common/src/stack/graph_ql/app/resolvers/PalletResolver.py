# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


from ariadne import ObjectType, QueryType, MutationType
import app.db as db

query = QueryType()
mutation = MutationType()

@query.field("pallet")
def resolve_pallet(*_):
    # TODO: rename rel as release
    results, _ = db.run_sql("SELECT id, name, version, rel, arch, os, url FROM rolls")
    return results

@mutation.field("addPallet")
def resolve_add_pallet(_, info, name, version, rel, arch, os, url=None):

    cmd = "INSERT INTO rolls (name, version, rel, arch, os, url) VALUES (%s, %s, %s, %s, %s, %s)"
    args = (name, version, rel, arch, os, url)
    db.run_sql(cmd, args)

    cmd = "SELECT id, name, version, rel, arch, os, url FROM rolls WHERE name=%s"
    args = (name,)
    result, _ = db.run_sql(cmd, args, fetchone=True)

    return result

@mutation.field("updatePallet")
def resolve_update_pallet(_, info, id, name=None, version=None, rel=None, arch=None, os=None, url=None):

    cmd = "SELECT id, name, version, rel, arch, os, url FROM rolls WHERE id=%s"
    args = (id,)
    pallet, _ = db.run_sql(cmd, args, fetchone=True)
    if not pallet:
        raise Exception("No pallet found")

    if not name and not version and not rel and not arch and not os:
        return pallet 

    update_params = []
    args = ()
    if name is not None:
        update_params.append('name="%s"')
        args += (name,)

    if version is not None:
        update_params.append('version="%s"')
        args += (version,)

    if rel is not None:
        update_params.append('rel="%s"')
        args += (rel,)

    if arch is not None:
        update_params.append('arch="%s"')
        args += (ach,)

    if os is not None:
        update_params.append('os="%s"')
        args += (os,)

    if url is not None:
        update_params.append('url="%s"')
        args += (url,)

    cmd = f'UPDATE rolls SET {",".join(update_params)}' + " WHERE id=%s"
    db.run_sql(cmd)

    cmd = "SELECT id, name, version, rel, arch, os, url FROM rolls WHERE id=%s"
    args = (id,)
    result, _ = db.run_sql(cmd, fetchone=True)

    return result

@mutation.field("deletePallet")
def resolve_delete_pallet(_, info, id):

    cmd = "DELETE FROM rolls WHERE id=%s"
    args = (id,)
    _, affected_rows = db.run_sql(cmd, args)

    if not affected_rows:
        return False

    return True

object_types = []

# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


from ariadne import ObjectType, QueryType, MutationType
import app.db as db

query = QueryType()
mutation = MutationType()


@query.field("pallets")
def resolve_pallets(*_):
    results, _ = db.run_sql("SELECT id, name, version, rel as 'release', arch, os, url FROM rolls")
    return results


@query.field("pallet")
def resolve_pallet(_, info, id):
    cmd = "SELECT id, name, version, rel as 'release', arch, os, url FROM rolls WHERE id=%s"
    args = (id,)
    result, _ = db.run_sql(cmd, args, fetchone=True)
    return result


@mutation.field("addPallet")
def resolve_add_pallet(_, info, name, version, release, arch, os, url=None):

    pallet_cmd = "SELECT id, name, version, rel as 'release', arch, os, url FROM rolls WHERE name=%s AND version=%s AND rel=%s AND arch=%s AND os=%s"
    pallet_args = (name, version, release, arch, os)

    pallet, _ = db.run_sql(pallet_cmd, pallet_args)
    if pallet:
        raise Exception("The pallet already exists")

    # Insert pallet
    cmd = "INSERT INTO rolls (name, version, rel, arch, os, url) VALUES (%s, %s, %s, %s, %s, %s)"
    args = (name, version, release, arch, os, url)
    db.run_sql(cmd, args)

    # Get the recently inserted value
    result, _ = db.run_sql(pallet_cmd, pallet_args, fetchone=True)
    return result

@mutation.field("updatePallet")
def resolve_update_pallet(obj, info, id, name=None, version=None, release=None, arch=None, os=None, url=None):
    pallet = resolve_pallet(obj, info, id)
    #check if pallet with id exists
    if not pallet:
        raise Exception("No pallet found")
    else:
        # check for duplicates
        name_new = name if name else pallet["name"]
        version_new = version if version else pallet["version"]
        release_new = release if release else pallet["release"]
        arch_new = arch if arch else pallet["arch"]
        os_new = os if os else pallet["os"]
        pallet_cmd = "SELECT id FROM rolls WHERE name=%s AND version=%s AND arch=%s AND rel=%s AND os=%s AND id!=%s" 
        pallet_args = (name_new, version_new, arch_new, release_new, os_new, id)
        _, affected_rows = db.run_sql(pallet_cmd, pallet_args)
        if affected_rows > 0:
            raise Exception("Pallet with new parameters already exists")

    update_params = []
    args = []
    if name:
        update_params.append('name=%s')
        args.append(name)

    if version:
        update_params.append('version=%s')
        args.append(version)

    if release:
        update_params.append('rel=%s')
        args.append(release)

    if arch:
        update_params.append('arch=%s')
        args.append(arch)

    if os:
        update_params.append('os=%s')
        args.append(os)

    if url:
        update_params.append('url=%s')
        args.append(url)

    cmd = f'UPDATE rolls SET {", ".join(update_params)} WHERE id=%s'
    args.append(id)
    db.run_sql(cmd, args)

    result = resolve_pallet(obj, info, id)
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

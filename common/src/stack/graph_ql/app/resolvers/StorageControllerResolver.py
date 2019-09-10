# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


from ariadne import ObjectType, QueryType, MutationType
import app.db as db

query = QueryType()
mutation = MutationType()


@query.field("storageControllers")
def resolve_storage_controllers(_, info, ID=None):
    cmd = """
            SELECT ID, scope_map_id, enclosure, adapter, slot, raidlevel, arrayid as arrayNumber, options 
            FROM storage_controller
        """
    args = []
    if ID:
        cmd += " WHERE ID = %s"
        args.append(ID)

    results, _ = db.run_sql(cmd, args)
    return results


@mutation.field("addStorageController")
def resolve_add_storage_controller(_, info, scopeMapId, enclosure, adapter, slot, raidlevel, arrayNumber, options=""):
    #TODO: make options nullable in db
    
    st_ctrl_cmd = """
            SELECT ID, scope_map_id, enclosure, adapter, slot, raidlevel, arrayid as arrayNumber, options 
            FROM storage_controller
            WHERE scope_map_id = %s AND enclosure = %s AND adapter = %s AND slot = %s AND raidlevel = %s AND arrayid = %s
        """
    st_ctrl_args = [scopeMapId, enclosure, adapter, slot, raidlevel, arrayNumber]
    _, affected_rows = db.run_sql(st_ctrl_cmd, st_ctrl_args)
    if affected_rows > 0:
        raise Exception(f"storage controller exists")

    # Insert storage controller
    args = st_ctrl_args + [options]
    cmd = """
            INSERT storage_controller (scope_map_id, enclosure, adapter, slot, raidlevel, arrayid, options)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
    db.run_sql(cmd, args)

    result, _ = db.run_sql(st_ctrl_cmd, st_ctrl_args, fetchone=True)
    return result


@mutation.field("updateStorageController")
def resolve_update_storage_controller(obj, info, ID, **kwargs):
    results = resolve_storage_controllers(obj, info, ID)
    if not results:
        raise Exception(f"storage controller with ID={ID} doesn't exist")

    params = []
    params.append('scope_map_id=%s') 
    params.append('enclosure=%s') 
    params.append('adapter=%s') 
    params.append('slot=%s') 
    params.append('raidlevel=%s') 
    params.append('arrayid=%s') 

    args = []
    args.append(kwargs.get("scopeMapId")) if kwargs.get("scopeMapId", None) else args.append(results[0]["scope_map_id"])
    args.append(kwargs.get("enclosure")) if kwargs.get("enclosure", None) else args.append(results[0]["enclosure"])
    args.append(kwargs.get("adapter")) if kwargs.get("adapter", None) else args.append(results[0]["adapter"])
    args.append(kwargs.get("slot")) if kwargs.get("slot", None) else args.append(results[0]["slot"])
    args.append(kwargs.get("raidlevel")) if kwargs.get("raidlevel", None) else args.append(results[0]["raidlevel"])
    args.append(kwargs.get("arrayNumber")) if kwargs.get("arrayNumber", None) else args.append(results[0]["arrayNumber"])
    args.append(ID)

    cmd = f"SELECT ID FROM storage_controller WHERE {' AND '.join(params)} AND ID!=%s"
    print(cmd)

    _, affected_rows = db.run_sql(cmd, args)
    if affected_rows > 0:
        raise Exception(f"storage controller with new parameters already exists")

    params = []
    args = []

    for key, value in kwargs.items():
        if key == 'scopeMapId':
            params.append('scope_map_id=%s')
        elif key == 'arrayNumber':
            params.append('arrayid=%s')
        else:
            params.append(f"{key}=%s")
        args.append(value)

    args.append(ID)
   
    cmd = f"UPDATE storage_controller SET {', '.join(params)} WHERE ID = %s"
    db.run_sql(cmd, args)

    results = resolve_storage_controllers(obj, info, ID)
    if results:
        return results[0]
    return None


@mutation.field("deleteStorageController")
def resolve_delete_storage_controller(_, info, ID):

    cmd = "DELETE FROM storage_controller WHERE ID=%s"
    args = (ID,)
    _, affected_rows = db.run_sql(cmd, args)

    if affected_rows:
        return True

    return False


object_types = []

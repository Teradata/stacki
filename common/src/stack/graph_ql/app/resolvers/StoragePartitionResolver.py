# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


from ariadne import ObjectType, QueryType, MutationType
import app.db as db

query = QueryType()
mutation = MutationType()


@query.field("storagePartitions")
def resolve_storage_partitions(_, info, ID=None):
    cmd = """
            SELECT ID, scope_map_id, device, mountpoint, size, fstype, partid as partNumber, options 
            FROM storage_partition
        """
    args = []
    if ID:
        cmd += " WHERE ID = %s"
        args.append(ID)

    results, _ = db.run_sql(cmd, args)
    return results


@mutation.field("addStoragePartition")
def resolve_add_storage_partition(_, info, scopeMapId, device, size, partNumber, fstype=None, mountpoint=None, options=""):
    #TODO: make options nullable in db

    st_part_cmd = """
            SELECT ID, scope_map_id, device, mountpoint, size, fstype, partid as partNumber, options
            FROM storage_partition
            WHERE scope_map_id = %s AND device = %s AND partid = %s
        """
    st_part_args = [scopeMapId, device, partNumber]
    _, affected_rows = db.run_sql(st_part_cmd, st_part_args)
    if affected_rows > 0:
        raise Exception(f"storage partition exists")

    # Insert storage partition
    cmd = """
            INSERT storage_partition (scope_map_id, device, mountpoint, size, fstype, partid, options)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
    args = [scopeMapId, device, mountpoint, size, fstype, partNumber, options]
    db.run_sql(cmd, args)

    result, _ = db.run_sql(st_part_cmd, st_part_args, fetchone=True)
    return result


@mutation.field("updateStoragePartition")
def resolve_update_storage_partition(obj, info, ID, **kwargs):
    results = resolve_storage_partitions(obj, info, ID)
    if not results:
        raise Exception(f"storage partition with ID={ID} doesn't exist")

    params = []
    params.append('scope_map_id=%s') 
    params.append('device=%s') 
    params.append('partid=%s') 

    args = []
    args.append(kwargs.get("scopeMapId")) if kwargs.get("scopeMapId", None) else args.append(results[0]["scope_map_id"])
    args.append(kwargs.get("device")) if kwargs.get("device", None) else args.append(results[0]["device"])
    args.append(kwargs.get("partNumber")) if kwargs.get("partNumber", None) else args.append(results[0]["partNumber"])
    args.append(ID)

    cmd = f"SELECT ID FROM storage_partition WHERE {' AND '.join(params)}  AND ID!=%s"
    _, affected_rows = db.run_sql(cmd, args)
    if affected_rows > 0:
        raise Exception(f"storage partition with new parameters already exists")


    params = []
    args = []

    for key, value in kwargs.items():
        if key == 'scopeMapId':
            params.append('scope_map_id=%s')
        elif key == 'partNumber':
            params.append('partid=%s')
        else:
            params.append(f"{key}=%s")
        args.append(value)
	
    args.append(ID)    
   
    cmd = f"UPDATE storage_partition SET {', '.join(params)} WHERE ID = %s"
    db.run_sql(cmd, args)

    results = resolve_storage_partitions(obj, info, ID)
    if results:
        return results[0]
    return None


@mutation.field("deleteStoragePartition")
def resolve_delete_storage_partition(_, info, ID):

    cmd = "DELETE FROM storage_partition WHERE ID=%s"
    args = (ID,)
    _, affected_rows = db.run_sql(cmd, args)

    if affected_rows:
        return True

    return False


object_types = []

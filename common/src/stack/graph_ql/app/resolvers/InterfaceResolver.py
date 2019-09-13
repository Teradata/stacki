# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


from ariadne import ObjectType, QueryType, MutationType
import app.db as db
from app.utils import map_kwargs


query = QueryType()
mutation = MutationType()
host = ObjectType("Host")

@host.field("interfaces")
def resolve_interfaces_from_node_id(parent, info):
    if parent is None or not parent.get("id"):
        return []

    cmd = """
    SELECT id, node as host, mac, ip, netmask, gateway,
        name, device, subnet, module, vlanid,
        options, channel, main
    FROM networks
    WHERE node=%s
    """
    args = [parent.get("id")]
    results, _ = db.run_sql(cmd, args)

    return results

@query.field("interfaces")
@map_kwargs({"id": "id_"})
def resolve_interfaces(_, info, id_=None, host_id=None, device=None):
    cmd = '''SELECT
        id,
        node AS host_id,
        mac,
        ip,
        name,
        device,
        subnet AS network_id,
        module,
        vlanid,
        options,
        channel,
        main
        FROM networks
        WHERE 1=1
'''

    args = ()
    if id_:
        cmd += ' AND id=%s '
        args += (id_, )
    # TODO error check -- node id and device must go together?  or maybe that's ok here?
    if host_id:
        cmd += ' AND node=%s '
        args += (host_id, )
    if device:
        cmd += ' AND device=%s '
        args += (device, )

    results, _ = db.run_sql(cmd, args)
    return results


@mutation.field("addInterface")
def resolve_add_interface(obj, info, host_id, device, network_id=None, name=None, mac=None, ip=None, module=None, vlanid=None, options=None, channel=None, main=None):
    # TODO need to do actual error checking
    # TODO names, ip's need to be unique across table
    # TODO no reason for interfaces table to have mask and gateway
    # TODO what is vlanid, can we kill it?
    if device in [interface["device"] for interface in resolve_interfaces(obj, info)]:
        raise Exception(f"interface {device} exists")

    cmd = "INSERT INTO networks (node, mac, ip, name, device, subnet, module, vlanid, options, channel, main) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    args = (host_id, mac, ip, name, device, network_id, module, vlanid, options, channel, main)
    results, _ = db.run_sql(cmd, args)

    # Get the recently inserted value
    # TODO should mutations return their own data?
    results = resolve_interfaces(obj, info, host_id=host_id, device=device)
    if results:
        return True
    return None

object_types = [host]

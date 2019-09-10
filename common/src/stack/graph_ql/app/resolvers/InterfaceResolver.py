# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


from ariadne import ObjectType, QueryType, MutationType
import app.db as db

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


object_types = [host]

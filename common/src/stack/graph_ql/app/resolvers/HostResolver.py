# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


from ariadne import ObjectType, QueryType, MutationType
import app.db as db

query = QueryType()
mutation = MutationType()
interface = ObjectType("Interface")

@query.field("hosts")
def resolve_hosts(_, info, id=None):
    # TODO: Add nested environment
    # TODO: Add nested osaction
    # TODO: Add nested installaction
    # TODO: Add nested attributes
    # TODO: Add nested appliance

    cmd = """
        SELECT id, name, rack, rank, comment, metadata,
        appliance AS appliance_id,
        box AS box_id,
        environment AS environment_id,
        osaction AS osaction_id,
        installaction AS installaction_id
        FROM nodes
        """
    args = ()

    if id:
        cmd += " WHERE id=%s"
        args += (id, )

    results, _ = db.run_sql(cmd, args)
    return results

@interface.field("host")
def resolve_host_by_id(parent, info):
    return resolve_hosts(parent, info, id=parent.get(id))[0]


object_types = [interface]

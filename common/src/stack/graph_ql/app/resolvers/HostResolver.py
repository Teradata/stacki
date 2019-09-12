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
def resolve_hosts(_, info):
    # TODO: Add nested environment
    # TODO: Add nested osaction
    # TODO: Add nested installaction
    # TODO: Add nested attributes
    # TODO: Add nested appliance

    cmd = """
        SELECT id, name, rack, rank, comment, metadata,
        appliance AS applianceId,
        box AS boxId,
        environment AS environmentId,
        osaction AS osactionId,
        installaction AS installactionId
        FROM nodes
        """
    args = []

    results, _ = db.run_sql(cmd, args)
    return results


@query.field("hostById")
def resolve_host_by_id(_, info, hostId):
    # TODO: Add nested environment
    # TODO: Add nested osaction
    # TODO: Add nested installaction
    # TODO: Add nested attributes
    # TODO: Add nested appliance

    cmd = """
        SELECT id, name, rack, rank, comment, metadata,
        appliance AS applianceId,
        box AS boxId,
        environment AS environmentId,
        osaction AS osactionId,
        installaction AS installactionId
        FROM nodes
        WHERE id=%s
        """
    args = [hostId]

    results, _ = db.run_sql(cmd, args, fetchone=True)
    return results


@interface.field("host")
def resolve_host_byId_from_parent(parent, info):
    return resolve_host_by_id(parent, info, hostId=parent.get("hostId"))


object_types = [interface]

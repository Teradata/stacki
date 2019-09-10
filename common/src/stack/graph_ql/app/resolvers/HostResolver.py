# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


from ariadne import ObjectType, QueryType, MutationType
import app.db as db

query = QueryType()
mutation = MutationType()


@query.field("hosts")
def resolve_hosts(*_):
    # TODO: Add nested environment
    # TODO: Add nested osaction
    # TODO: Add nested installaction
    # TODO: Add nested attributes

    cmd = """
        SELECT id, name, rack, rank, comment, metadata,
        appliance AS appliance_id,
        box AS box_id,
        environment AS environment_id,
        osaction AS osaction_id,
        installaction AS installaction_id
        from nodes
        """
    args = []

    results, _ = db.run_sql(cmd, args)
    return results


object_types = []

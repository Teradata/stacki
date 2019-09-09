# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


from ariadne import ObjectType, QueryType, MutationType
import app.db as db

query = QueryType()
mutation = MutationType()

@query.field("bootname")
def resolve_bootname(*_):
    results, _ = db.run_sql("SELECT id, name, type FROM bootnames")
    return results

object_types = []
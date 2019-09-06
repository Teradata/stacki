# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


from ariadne import (
    ObjectType,
    QueryType,
    MutationType,
    SubscriptionType,
    gql,
    make_executable_schema,
    load_schema_from_path,
)
from ariadne.asgi import GraphQL
import pkgutil


from . import db

# TODO: Make this dynamic
type_defs = load_schema_from_path("./app/schema/")


query_fields = []
mutation_fields = []
object_fields = []

for finder, name, ispkg in pkgutil.walk_packages(["./app/resolvers"]):
    _module = finder.find_module(name).load_module(name)
    query_fields.append(_module.query)
    mutation_fields.append(_module.mutation)
    object_fields.extend(_module.object_types)

schema = make_executable_schema(
    type_defs, query_fields + mutation_fields + object_fields
)

# Create an ASGI app using the schema, running in debug mode
app = GraphQL(schema)


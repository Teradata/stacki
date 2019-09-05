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
import asyncio
import requests
import importlib
import pathlib
import pkgutil


from . import db
from .resolvers import BoxResolver, ApplianceResolver, OSResolver


type_defs = load_schema_from_path("./app/schema/")


query_fields = [] + [BoxResolver.query, ApplianceResolver.query, OSResolver.query]
mutation_fields = [] + [
    BoxResolver.mutations,
    ApplianceResolver.mutations,
    OSResolver.mutations,
]
object_fields = [] + [OSResolver.box]

schema = make_executable_schema(
    type_defs, query_fields + mutation_fields + object_fields
)

# Create an ASGI app using the schema, running in debug mode
app = GraphQL(schema)


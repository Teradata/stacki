from ariadne import ObjectType, QueryType, SubscriptionType, gql, make_executable_schema, load_schema_from_path
from ariadne.asgi import GraphQL
from stack.db import db
import asyncio

# Define types using Schema Definition Language (https://graphql.org/learn/schema/)
# Wrapping string in gql function provides validation and better error traceback
type_defs = load_schema_from_path("/opt/stack/lib/python3.7/site-packages/stack/graph_ql/schema/")

# Create executable GraphQL schema
schema = make_executable_schema(type_defs)

# Create an ASGI app using the schema, running in debug mode
app = GraphQL(schema, debug=True)

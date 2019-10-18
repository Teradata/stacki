from ariadne import MutationType, QueryType

from stack.graphql.utils import dynamic_import


# Roots of the graph
query = QueryType()
mutation = MutationType()
object_types = []


# Mutation results
def error(message):
	return {
		"success": False,
		"error": message
	}

def success(**kwargs):
	fields = {
		"success": True
	}

	if kwargs:
		fields.update(kwargs)

	return fields

# Dynamically pull in all the resolvers in this folder
dynamic_import(__file__, __name__)

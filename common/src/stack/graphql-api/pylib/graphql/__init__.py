import logging
from pathlib import Path
import re
import sys
import time

from ariadne import graphql_sync, load_schema_from_path, make_executable_schema
from pymysql.cursors import DictCursor

from stack.graphql.resolvers import mutation, object_types, query


# Disable Ariadne's default logging
logger = logging.getLogger("ariadne")
logger.setLevel(logging.CRITICAL)

# Set up the GraphQL schema
type_defs = load_schema_from_path(Path(__file__).parent / "schema")
schema = make_executable_schema(type_defs, [query, mutation])

def _debug_execute(func, mogrify):
	def wrapper(*args, **kwargs):
		# Get the query to be executed and format it nicely
		query = re.sub(r"^\s+", "", mogrify(*args, **kwargs), flags=re.MULTILINE).strip()

		# Write it out to stderr
		print(f"{'-'*40}\nGraphQL query:\n\n{query}\n", file=sys.stderr)

		# Then actually execute it
		start_time = time.time()
		count = func(*args, **kwargs)
		elapsed = round(time.time() - start_time, 4)

		rows = "row" if count == 1 else "rows"
		print(f"Affected: {count} {rows} in {elapsed} seconds", file=sys.stderr)
		print(f"{'-'*40}\n", file=sys.stderr)

		return count

	return wrapper

def execute(connection, data, debug=False):
	cursor = connection.cursor(DictCursor)
	if debug:
		cursor.execute = _debug_execute(cursor.execute, cursor.mogrify)

	success, result = graphql_sync(
		schema,
		data,
		context_value=cursor
	)
	cursor.close()

	return success, result

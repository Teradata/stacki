from pymysql import IntegrityError

from stack.graphql.resolvers import error, mutation, query, success
from stack.graphql.utils import map_kwargs, create_common_filters


@query.field("appliances")
@map_kwargs({"id": "id_"})
def appliances(obj, info, id_=None, names=None):
	query = "SELECT id, name, public FROM appliances"
	filters, values = create_common_filters(id_, names)

	if filters:
		query += " WHERE " + " AND ".join(filters)

	query += " ORDER BY id"

	info.context.execute(query, values)
	return info.context.fetchall()


@query.field("appliances_exist")
def appliances_exist(obj, info, names=None):
	lookups = []

	if names:
		# Get a count of how many appliances match the name pattern
		query = "(" + ") UNION ALL (".join([
			f"SELECT COUNT(id) FROM appliances WHERE name LIKE %s"
			for name in names
		]) + ")"

		info.context.execute(query, names)

		# Gather up the lookup results
		for name, row in zip(names, info.context.fetchall()):
			lookups.append({
				"name": name,
				"exists": row["COUNT(id)"] != 0
			})

	return lookups


@mutation.field("add_appliance")
def add_appliance(obj, info, name, public="yes"):
	# No blank names
	if not name.strip():
		return error("appliance name can not be blank")

	try:
		# Insert the data
		info.context.execute(
			"INSERT INTO appliances (name, public) VALUES (%s, %s)",
			[name, public]
		)

		# Return the new row
		info.context.execute("""
			SELECT id, name, public FROM appliances
			WHERE id=LAST_INSERT_ID()
		""")

		return success(appliance=info.context.fetchone())

	# Name wasn't unique
	except IntegrityError:
		return error(f'appliance "{name}" already exists')


@mutation.field("remove_appliance")
@map_kwargs({"id": "id_"})
def remove_appliance(obj, info, id_=None, names=None):
	# Not being given a remove target is a no-op
	if id_ or names:
		# Get the data for the appliance names we are trying to remove
		target_appliances = {
			a["name"] for a in appliances(obj, info, names=names)
		}

		# If nothing matched then we are done
		if not target_appliances:
			return success()

		# Make sure we aren't removing the default appliance
		if "backend" in target_appliances:
			return error("cannot remove default appliance")

		# We also can't remove any appliances in use
		info.context.execute("""
			SELECT DISTINCT appliances.name FROM nodes, appliances
			WHERE nodes.appliance = appliances.id
		""")

		host_appliances = {
			a["name"] for a in info.context.fetchall()
		}

		appliances_in_use = ', '.join(target_appliances.intersection(host_appliances))
		if appliances_in_use:
			return error(f"cannot remove in-use appliances: {appliances_in_use}")

		# Safe to delete the appliances
		query = "DELETE FROM appliances"
		filters, values = create_common_filters(id_, names)

		if filters:
			query += " WHERE " + " AND ".join(filters)

		info.context.execute(query, values)

	return success()

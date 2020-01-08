from collections import defaultdict

from stack.graphql.resolvers.plugins import registry


@registry.plugin("attributes")
def host_constants(cursor, scope, targets):
	results = defaultdict(dict)

	def _add_result(target, name, value):
		results[target][name] = {
			"target": target,
			"scope": "host",
			"type": "const",
			"name": name,
			"value": value
		}

	if scope == "host":
		# Get a bunch of data about each host
		seen_boxes = defaultdict(list)

		cursor.execute("""
			SELECT
				nodes.name AS hostname,
				appliances.name AS appliance,
				boxes.id AS box_id,
				boxes.name AS box,
				oses.name AS os,
				environments.name AS environment,
				nodes.rack,
				nodes.rank,
				nodes.metadata
			FROM nodes
			INNER JOIN appliances ON appliances.id = nodes.appliance
			INNER JOIN boxes ON boxes.id = nodes.box
			INNER JOIN oses ON oses.id = boxes.os
			LEFT JOIN environments ON environments.id = nodes.environment
			WHERE nodes.name IN %s
		""", (targets,))

		for row in cursor.fetchall():
			_add_result(row["hostname"], "hostname", row["hostname"])
			_add_result(row["hostname"], "appliance", row["appliance"])
			_add_result(row["hostname"], "box", row["box"])
			_add_result(row["hostname"], "os", row["os"])

			if row["environment"]:
				_add_result(row["hostname"], "environment", row["environment"])

			_add_result(row["hostname"], "rack", row["rack"])
			_add_result(row["hostname"], "rank", row["rank"])

			if row["metadata"]:
				_add_result(row["hostname"], "metadata", row["metadata"])

			seen_boxes[row["box_id"]].append(row["hostname"])

		# Now figure out the pallets and carts for every box seen
		for box_id in seen_boxes:
			# First the pallets
			pallets = []
			os_version = None

			cursor.execute("""
				SELECT name, version, rel, os FROM rolls
				INNER JOIN stacks ON stacks.roll = rolls.id
				WHERE stacks.box = %s
			""", (box_id,))

			for row in cursor.fetchall():
				pallets.append(f"{row['name']}-{row['version']}-{row['rel']}")

				# Calculate the "os.version" attr with format "{major_version}.x"
				if row["name"] in {"SLES", "CentOS", "RHEL", "Ubuntu", "Ubuntu-Server", "Fedora"}:
					# Strip the OS name off the release to get the major version number
					if row["rel"].startswith(row["os"]):
						os_version = f"{row['rel'][len(row['os']):]}.x"
					# Fedora's OS is 'redhat'
					elif row["rel"].startswith(row["name"].lower()):
						os_version = f"{row['rel'][len(row['name']):]}.x"

			# Then the carts
			cursor.execute("""
				SELECT name FROM carts
				INNER JOIN cart_stacks ON cart_stacks.cart = carts.id
				WHERE cart_stacks.box = %s
			""", (box_id,))

			carts = [row["name"] for row in cursor.fetchall()]

			for hostname in seen_boxes[box_id]:
				_add_result(hostname, "pallets", str(pallets))
				_add_result(hostname, "os.version", os_version)
				_add_result(hostname, "carts", str(carts))

		# Get some network info for the hosts
		cursor.execute("""
			SELECT nodes.name AS hostname, subnets.zone, networks.ip AS address
			FROM nodes
			INNER JOIN networks ON networks.node = nodes.id
			INNER JOIN subnets ON subnets.id = networks.subnet
			WHERE networks.main = true
			AND nodes.name IN %s
		""", (targets,))

		for row in cursor.fetchall():
			_add_result(row["hostname"], "domainname", row["zone"])
			if row["address"]:
				_add_result(row["hostname"], "hostaddr", row["address"])

		# And finally any groups the hosts are members of
		host_groups = defaultdict(list)
		cursor.execute("""
			SELECT nodes.name AS hostname, groups.name AS group_name
			FROM groups
			INNER JOIN memberships ON memberships.groupid = groups.id
			INNER JOIN nodes ON nodes.id = memberships.nodeid
			WHERE nodes.name IN %s
			ORDER BY group_name
		""", (targets,))

		for row in cursor.fetchall():
			host_groups[row["hostname"]].append(row["group_name"])
			_add_result(row["hostname"], f"group.{row['group_name']}", "true")

		for hostname, groups in host_groups.items():
			_add_result(hostname, "groups", " ".join(groups))

	return results

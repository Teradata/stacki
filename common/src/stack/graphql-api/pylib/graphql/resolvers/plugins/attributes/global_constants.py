from collections import defaultdict
from ipaddress import IPv4Network

import stack
from stack.graphql.resolvers.plugins import registry


@registry.plugin("attributes")
def global_constants(cursor, scope, targets):
	results = defaultdict(dict)

	def _add_result(name, value):
		for target in targets:
			results[target][name] = {
				"target": target,
				"scope": "global",
				"type": "const",
				"name": name,
				"value": value
			}

	if scope in ["global", "host"] and targets:
		cursor.execute("""
			SELECT networks.ip,
			IF(networks.name IS NOT NULL, networks.name, nodes.name) AS hostname,
			subnets.zone, subnets.address, subnets.mask, subnets.name AS netname
			FROM networks
			INNER JOIN subnets ON subnets.id = networks.subnet
			INNER JOIN nodes ON nodes.id = networks.node
			INNER JOIN appliances ON appliances.id = nodes.appliance
			WHERE appliances.name = 'frontend'
			AND (subnets.name = 'public' OR subnets.name = 'private')
		""")

		for row in cursor.fetchall():
			network = IPv4Network(f"{row['address']}/{row['mask']}")

			if row["netname"] == "private":
				_add_result("Kickstart_PrivateKickstartHost", row["ip"])
				_add_result("Kickstart_PrivateAddress", row["ip"])
				_add_result("Kickstart_PrivateHostname", row["hostname"])
				_add_result("Kickstart_PrivateDNSDomain", row["zone"])
				_add_result("Kickstart_PrivateNetwork", row["address"])
				_add_result("Kickstart_PrivateNetmask", row["mask"])
				_add_result("Kickstart_PrivateNetmaskCIDR", str(network.prefixlen))
			elif row["netname"] == "public":
				_add_result("Kickstart_PublicAddress", row["ip"])
				_add_result("Kickstart_PublicHostname", f"{row['hostname']}.{row['zone']}")
				_add_result("Kickstart_PublicDNSDomain", row["zone"])
				_add_result("Kickstart_PublicNetwork", row["address"])
				_add_result("Kickstart_PublicNetmask", row["mask"])
				_add_result("Kickstart_PublicNetmaskCIDR", str(network.prefixlen))

		# Add in the Stacki version info
		_add_result("release", stack.release)
		_add_result("version", stack.version)

	return results

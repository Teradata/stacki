# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import stack.mq
from stack.util import flatten

from ipaddress import IPv4Network


class Plugin(stack.commands.Plugin):
	"""
	Output intrinstic attrs for global scope
	"""

	def provides(self):
		return 'global_intrinsic'

	def run(self, scope_mappings):
		# Figure out the output targets
		node_ids = []
		targets = []
		for scope_mapping in scope_mappings:
			# We only need to run for host or global scope
			if scope_mapping.scope == 'host':
				node_ids.append(scope_mapping.node_id)
			elif scope_mapping.scope == 'global':
				targets.append('')
			else:
				continue

		if node_ids:
			targets.extend(flatten(self.db.select(
				'nodes.name FROM nodes WHERE nodes.id IN %s',
				(node_ids,)
			)))

		# Get various kickstart networking data
		output_rows = []
		if targets:
			for ip, hostname, zone, address, netmask, network_name in self.db.select("""
				networks.ip, IF(networks.name IS NOT NULL, networks.name, nodes.name),
				subnets.zone, subnets.address, subnets.mask, subnets.name
				FROM networks
				INNER JOIN subnets ON subnets.id = networks.subnet
				INNER JOIN nodes ON nodes.id = networks.node
				INNER JOIN appliances ON appliances.id = nodes.appliance
				WHERE appliances.name = 'frontend'
				AND (subnets.name = 'public' OR subnets.name = 'private')
			"""):
				network = IPv4Network(f"{address}/{netmask}")

				if network_name == 'private':
					for target in targets:
						output_rows.append([target, 'global', 'const', 'Kickstart_PrivateKickstartHost', ip])
						output_rows.append([target, 'global', 'const', 'Kickstart_PrivateAddress', ip])
						output_rows.append([target, 'global', 'const', 'Kickstart_PrivateHostname', hostname])
						output_rows.append([target, 'global', 'const', 'Kickstart_PrivateDNSDomain', zone])
						output_rows.append([target, 'global', 'const', 'Kickstart_PrivateNetwork', address])
						output_rows.append([target, 'global', 'const', 'Kickstart_PrivateNetmask', netmask])
						output_rows.append([target, 'global', 'const', 'Kickstart_PrivateNetmaskCIDR', str(network.prefixlen)])
				elif network_name == 'public':
					for target in targets:
						output_rows.append([target, 'global', 'const', 'Kickstart_PublicAddress', ip])
						output_rows.append([target, 'global', 'const', 'Kickstart_PublicHostname', f'{hostname}.{zone}'])
						output_rows.append([target, 'global', 'const', 'Kickstart_PublicDNSDomain', zone])
						output_rows.append([target, 'global', 'const', 'Kickstart_PublicNetwork', address])
						output_rows.append([target, 'global', 'const', 'Kickstart_PublicNetmask', netmask])
						output_rows.append([target, 'global', 'const', 'Kickstart_PublicNetmaskCIDR', str(network.prefixlen)])

			# Add in the Stacki version info
			for target in targets:
				output_rows.append([target, 'global', 'const', 'release', stack.release])
				output_rows.append([target, 'global', 'const', 'version', stack.version])

		return output_rows

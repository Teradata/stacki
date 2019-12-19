# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from collections import defaultdict

import stack.commands
import stack.mq
from stack.util import flatten


class Plugin(stack.commands.Plugin):
	"""
	Output intrinstic attrs for host scope
	"""

	def provides(self):
		return 'host_intrinsic'

	def run(self, scope_mappings):
		# Figure out the output targets
		node_ids = []
		for scope_mapping in scope_mappings:
			# We only need to run for host scope
			if scope_mapping.scope == 'host':
				node_ids.append(scope_mapping.node_id)
			else:
				continue

		output_rows = []
		box_map = defaultdict(list)
		hostname_map = {}

		# Get the data for the hosts
		if node_ids:
			for node_id, hostname, appliance, box_id, box, os, environment, rack, rank, metadata in self.db.select("""
				nodes.id, nodes.name, appliances.name, boxes.id, boxes.name, oses.name,
				environments.name, nodes.rack, nodes.rank, nodes.metadata
				FROM nodes
				INNER JOIN appliances ON appliances.id = nodes.appliance
				INNER JOIN boxes ON boxes.id = nodes.box
				INNER JOIN oses ON oses.id = boxes.os
				LEFT JOIN environments ON environments.id = nodes.environment
				WHERE nodes.id IN %s
			""", (node_ids,)):
				output_rows.append([hostname, 'host', 'const', 'hostname', hostname])
				output_rows.append([hostname, 'host', 'const', 'appliance', appliance])
				output_rows.append([hostname, 'host', 'const', 'box', box])
				output_rows.append([hostname, 'host', 'const', 'os', os])

				if environment:
					output_rows.append([hostname, 'host', 'const', 'environment', environment])

				output_rows.append([hostname, 'host', 'const', 'rack', rack])
				output_rows.append([hostname, 'host', 'const', 'rank', rank])

				if metadata:
					output_rows.append([hostname, 'host', 'const', 'metadata', metadata])

				# Add the host to the box map
				box_map[box_id].append(hostname)

				# And to the hostname map
				hostname_map[node_id] = hostname

			# Now figure out the pallets and carts for every box seen
			for box_id in box_map:
				# First the pallets
				pallets = []
				os_version = None
				for name, version, rel, pallet_os in self.db.select("""
					rolls.name, rolls.version, rolls.rel, rolls.os
					FROM rolls
					INNER JOIN stacks ON stacks.roll = rolls.id
					WHERE stacks.box = %s
				""", (box_id,)):
					pallets.append(f"{name}-{version}-{rel}")
					if name in ['SLES', 'CentOS', 'RHEL', 'Ubuntu', 'Ubuntu-Server', 'Fedora', 'openSUSE']:
						# the attr os.version is '{major_version}.x'
						# release is now '{OS}{major_version}'
						if pallet_os in rel:
							os_version = f'{rel.replace(pallet_os, "")}.x'
						# fedora's OS is 'redhat' ...
						elif name.lower() in rel:
							os_version = f'{rel.replace(name.lower(), "")}.x'

				for hostname in box_map[box_id]:
					output_rows.append([hostname, 'host', 'const', 'pallets', pallets])
					output_rows.append([hostname, 'host', 'const', 'os.version', os_version])

				# Then the carts
				carts = flatten(self.db.select("""
					carts.name
					FROM carts
					INNER JOIN cart_stacks ON cart_stacks.cart = carts.id
					WHERE cart_stacks.box = %s
				""", (box_id,)))

				for hostname in box_map[box_id]:
					output_rows.append([hostname, 'host', 'const', 'carts', carts])

			# Get some network info for the hosts
			for node_id, zone, address in self.db.select("""
				networks.node, subnets.zone, networks.ip
				FROM networks
				INNER JOIN subnets ON networks.subnet=subnets.id
				WHERE networks.main = true
				AND networks.node IN %s
			""", (node_ids,)):
				output_rows.append([hostname_map[node_id], 'host', 'const', 'domainname', zone])

				if address:
					output_rows.append([hostname_map[node_id], 'host', 'const', 'hostaddr', address])

			# And finally any groups the hosts are in
			groups = defaultdict(list)
			for node_id, group in self.db.select("""
				memberships.nodeid, groups.name
				FROM groups
				INNER JOIN memberships ON memberships.groupid=groups.id
				WHERE memberships.nodeid IN %s
				ORDER BY groups.name
			""", (node_ids,)):
				groups[node_id].append(group)
				output_rows.append([hostname_map[node_id], 'host', 'const', f'group.{group}', 'true'])

			for node_id in node_ids:
				output_rows.append([hostname_map[node_id], 'host', 'const', 'groups', ' '.join(groups[node_id])])

		return output_rows

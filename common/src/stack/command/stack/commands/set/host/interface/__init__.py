# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from collections import defaultdict

import stack.commands
from stack.exception import CommandError


class command(stack.commands.set.host.command):
	def validate(self, hosts, interface=None, mac=None, network=None):
		"""
		Validated that the provided interface, mac, and/or network
		exist for the hosts, or raise an error.
		"""

		# Construct our host data to check against
		host_data = defaultdict(lambda: defaultdict(set))
		for row in self.call('list.host.interface', hosts):
			combo = []
			if row['interface']:
				host_data[row['host']]['interfaces'].add(row['interface'])
				combo.append(row['interface'])

			if row['mac']:
				host_data[row['host']]['macs'].add(row['mac'])
				combo.append(row['mac'])

			if row['network']:
				host_data[row['host']]['networks'].add(row['network'])
				combo.append(row['network'])

			if len(combo) > 1:
				host_data[row['host']]['combos'].add(tuple(combo))

		# Our combination the user asked for
		combo = tuple(filter(None, (interface, mac, network)))

		# Check the provided arguements against the host data
		for host in hosts:
			if interface and interface not in host_data[host]['interfaces']:
				raise CommandError(self, f'interface "{interface}" does not exist for host "{host}"')

			if mac and mac not in host_data[host]['macs']:
				raise CommandError(self, f'mac "{mac}" does not exist for host "{host}"')

			if network and network not in host_data[host]['networks']:
				raise CommandError(self, f'network "{network}" does not exist for host "{host}"')

			if len(combo) > 1 and combo not in host_data[host]['combos']:
				combo_join = ', '.join(combo)
				raise CommandError(self, f'combination of "{combo_join}" does not exist for host "{host}"')

# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import stack.mq


class Plugin(stack.commands.Plugin):
	"""
	Output intrinstic firewall rules for each network
	"""

	def run(self, node_id):
		# Get the host name and appliance type for the node_id
		host, appliance = self.db.select("""
			nodes.name, appliances.name FROM nodes, appliances
			WHERE nodes.id = %s AND nodes.appliance = appliances.id
		""", (node_id,))[0]

		# We generate different rules for frontends and everything else
		if appliance == 'frontend':
			for network in self.owner.call('list.network'):
				if network['pxe']:
					# TCP ports for installing backends
					self.owner.addOutput(host, (
						f'STACKI-INSTALLATION-{network["network"]}',
						'filter',
						f'http,https,3825,{stack.mq.ports.subscribe}'
						f',{stack.mq.ports.control}', 'tcp', 'INPUT',
						'ACCEPT', network['network'], None, '-m multiport',
						f'Accept Stacki traffic on {network["network"]}'
						' network - Intrinsic rule', 'G', 'const'
					))

					# UDP ports for TFTP for backends
					self.owner.addOutput(host, (
						f'STACKI-TFTP-{network["network"]}', 'filter',
						'tftp,bootps,bootpc', 'udp', 'INPUT', 'ACCEPT',
						network['network'], None, '-m multiport',
						'Accept UDP traffic for TFTP on'
						f' {network["network"]} network - Intrinsic rule',
						'G', 'const'
					))

					# UDP port for SMQ publisher
					self.owner.addOutput(host, (
						f'STACKI-MQ-PUBLISH-PORT-{network["network"]}',
						'filter', str(stack.mq.ports.publish), 'udp',
						'INPUT', 'ACCEPT', network['network'], None, '',
						'Accept UDP traffic for SMQ publisher on'
						f' {network["network"]} network - Intrinsic rule',
						'G', 'const'
					))
					# UDP port for NTP service
					self.owner.addOutput(host, (
						f'STACKI-NTP-{network["network"]}',
						'filter', 'ntp', 'udp',
						'INPUT', 'ACCEPT', network['network'], None, '',
						'Accept UDP traffic for NTP on'
						f' {network["network"]} network - Intrinsic rule',
						'G', 'const'
					))

				if network['dns']:
					# DNS gets a special rule to let its traffic in
					self.owner.addOutput(host, (
						f'STACKI-DNS-{network["network"]}',
						'filter', 'domain', 'all',
						'INPUT', 'ACCEPT', network['network'], None,
						f'-s {network["address"]}/{network["mask"]}',
						f'Accept DNS traffic on {network["network"]} '
						'network - Intrinsic rule', 'G', 'const'
					))
		else:
			# We'll need a list of frontend ips for each network
			frontend_ips = {
				row['network']: row['ip']
				for row in self.owner.call('list.host.interface', ['localhost'])
				if row['network'] and row['ip']
			}

			for network in self.owner.call('list.network'):
				if network['pxe'] and network['network'] in frontend_ips:
					# All traffic from the frontend is allowed
					self.owner.addOutput(host, (
						f'STACKI-FRONTEND-INGRESS-{network["network"]}',
						'filter', 'all', 'all', 'INPUT', 'ACCEPT',
						network['network'], None,
						f'-s {frontend_ips[network["network"]]}',
						'Accept all frontend traffic on '
						f'{network["network"]} network - Intrinsic rule',
						'G', 'const'
					))

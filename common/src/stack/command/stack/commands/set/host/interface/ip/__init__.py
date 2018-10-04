# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import ipaddress

import stack.commands
from stack.exception import ParamRequired, CommandError


class Command(stack.commands.set.host.interface.command):
	"""
	Sets the IP address for the named interface for one host.

	<arg type='string' name='host' optional='0'>
	A single host.
	</arg>

	<param type='string' name='interface'>
	Name of the interface.
	</param>

	<param type='string' name='mac'>
	MAC address of the interface.
	</param>

	<param type='string' name='network'>
	Network name of the interface.
	</param>

	<param type='string' name='ip' optional='0'>
	The IP address to set. Use ip=AUTO to let the system pick one for
	you or ip=NULL to clear the IP address.
	</param>

	<example cmd='set host interface ip backend-0-0 interface=eth1 ip=192.168.0.10'>
	Sets the IP Address for the eth1 device on host backend-0-0.
	</example>
	"""

	def run(self, params, args):
		host = self.getSingleHost(args)

		(ip, interface, mac, network) = self.fillParams([
			('ip', None, True),
			('interface', None),
			('mac', None),
			('network', None)
		])

		# Gotta have one of these
		if not any([interface, mac, network]):
			raise ParamRequired(self, ('interface', 'mac', 'network'))

		# Make sure interface, mac, and/or network exist on our host
		self.validate([host], interface, mac, network)

		# If ip is an empty sting or NULL, we are clearing it
		if not ip or ip.upper() == 'NULL':
			ip = None

		# See if we are picking the next IP address
		if ip and ip.upper() == 'AUTO':
			# We gotta have a network to get the IP space
			if not network:
				for row in self.call('list.host.interface', []):
					if (
						(interface and row['interface'] == interface) or
						(mac and row['mac'] == mac)
					):
						network = row['network']
						break

				# Make sure we were successful at getting a network
				if not network:
					raise CommandError(self, 'unknown network for interface')

			# Now get our IP space
			data = self.call('list.network', [network])[0]
			ip_space = ipaddress.IPv4Network(f"{data['address']}/{data['mask']}")

			# And a set of all IPs already in use on this network
			existing = {
				row['ip']
				for row in self.call('list.host.interface', [])
				if row['network'] == network
			}

			# It would be bad to trample the gateway
			if data['gateway']:
				existing.add(data['gateway'])

			# Now run through the IP space and find the first unused IP
			ip = None
			for address in ip_space.hosts():
				if str(address) not in existing:
					ip = str(address)
					break

			# Error out if we couldn't find a free IP
			if not ip:
				raise CommandError(self, 'no free ip addresses left in the network')

		# Make the change in the DB
		if network:
			sql = """
				update networks,nodes,subnets set networks.ip=%s
				where nodes.name=%s and subnets.name=%s
				and networks.node=nodes.id and networks.subnet=subnets.id
			"""
			values = [ip, host, network]
		else:
			sql = """
				update networks,nodes set networks.ip=%s
				where nodes.name=%s and networks.node=nodes.id
			"""
			values = [ip, host]

		if interface:
			sql += " and networks.device=%s"
			values.append(interface)

		if mac:
			sql += " and networks.mac=%s"
			values.append(mac)

		self.db.execute(sql, values)

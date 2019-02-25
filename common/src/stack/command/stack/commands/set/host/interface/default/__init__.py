# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ParamRequired


class Command(stack.commands.set.host.interface.command):
	"""
	Designates one network as the default route for a set of hosts.
	Either the interface, mac, or network paramater is required.

	<arg type='string' name='host' repeat='1' optional='0'>
	One or more hosts.
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

	<param type='boolean' name='default' optional='1'>
	Can be used to set the value of default to False.
	</param>
	"""

	def run(self, params, args):
		hosts = self.getHosts(args)

		(default, interface, mac, network) = self.fillParams([
			('default', 'true'),
			('interface', None),
			('mac', None),
			('network', None)
		])

		default = self.str2bool(default)

		# Gotta have one of these
		if not any([interface, mac, network]):
			raise ParamRequired(self, ('interface', 'mac', 'network'))

		# Make sure interface, mac, and/or network exist on our hosts
		self.validate(hosts, interface, mac, network)

		for host in hosts:
			if default:
				# Clear the old default
				self.db.execute("""
					update networks,nodes set networks.main=0
					where nodes.name=%s and networks.node=nodes.id
				""", (host,))

			# Set the new default value (might be 0 or 1)
			if network:
				sql = """
					update networks,nodes,subnets set networks.main=%s
					where nodes.name=%s and subnets.name=%s
					and networks.node=nodes.id and networks.subnet=subnets.id
				"""
				values = [default, host, network]
			else:
				sql = """
					update networks,nodes set networks.main=%s
					where nodes.name=%s and networks.node=nodes.id
				"""
				values = [default, host]

			if interface:
				sql += " and networks.device=%s"
				values.append(interface)

			if mac:
				sql += " and networks.mac=%s"
				values.append(mac)

			self.db.execute(sql, values)

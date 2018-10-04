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

import stack.commands
from stack.exception import ParamRequired


class Command(stack.commands.set.host.interface.command):
	"""
	Sets the logical interface of a mac address for particular hosts.

	<arg type='string' name='host' repeat='1' optional='0'>
	One or more hosts.
	</arg>

	<param type='string' name='interface' optional='0'>
	Name of the interface.
	</param>

	<param type='string' name='mac'>
	MAC address of the interface.
	</param>

	<param type='string' name='network'>
	Network name of the interface.
	</param>

	<example cmd='set host interface interface backend-0-0 00:0e:0c:a7:5d:ff eth1'>
	Sets the logical interface of MAC address 00:0e:0c:a7:5d:ff to be eth1
	</example>

	<example cmd='set host interface interface backend-0-0 interface=eth1 mac=00:0e:0c:a7:5d:ff'>
	Same as above.
	</example>
	"""

	def run(self, params, args):
		hosts = self.getHosts(args)

		(interface, mac, network) = self.fillParams([
			('interface', None, True),
			('mac', None),
			('network', None)
		])

		# Gotta have one of these
		if not any([mac, network]):
			raise ParamRequired(self, ('mac', 'network'))

		# Make sure mac and/or network exist on our hosts
		self.validate(hosts, None, mac, network)

		for host in hosts:
			if network:
				sql = """
					update networks,nodes,subnets set networks.device=%s
					where nodes.name=%s and subnets.name=%s
					and networks.node=nodes.id and networks.subnet=subnets.id
				"""
				values = [interface, host, network]
			else:
				sql = """
					update networks,nodes set networks.device=%s
					where nodes.name=%s and networks.node=nodes.id
				"""
				values = [interface, host]

			if mac:
				sql += " and networks.mac=%s"
				values.append(mac)

			self.db.execute(sql, values)

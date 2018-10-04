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
	Sets the network for named interface on one of more hosts.

	<arg type='string' name='host' repeat='1' optional='0'>
	One or more hosts.
	</arg>

	<param type='string' name='interface'>
	Name of the interface.
	</param>

	<param type='string' name='mac'>
	MAC address of the interface.
	</param>

	<param type='string' name='network' optional='0'>
	Network name of the interface.
	</param>

	<example cmd='set host interface network backend-0-0 interface=eth1 network=public'>
	Sets eth1 to be on the public network.
	</example>
	"""

	def run(self, params, args):
		hosts = self.getHosts(args)

		(interface, mac, network) = self.fillParams([
			('interface', None),
			('mac', None),
			('network', None, True)
		])

		# Gotta have one of these
		if not any([interface, mac]):
			raise ParamRequired(self, ('interface', 'mac'))

		# Make sure interface and/or mac exist on our hosts
		self.validate(hosts, interface, mac, None)

		for host in hosts:
			sql = """
				update networks,nodes set networks.subnet=(
					select id from subnets where subnets.name=%s
				)
				where nodes.name=%s and networks.node=nodes.id
			"""
			values = [network, host]

			if interface:
				sql += " and networks.device=%s"
				values.append(interface)

			if mac:
				sql += " and networks.mac=%s"
				values.append(mac)

			self.db.execute(sql, values)

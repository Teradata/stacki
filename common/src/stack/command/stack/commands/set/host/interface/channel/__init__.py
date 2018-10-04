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
	Sets the channel for a named interface.

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

	<param type='string' name='channel' optional='0'>
	The channel for an interface. Use channel=NULL to clear.
	</param>

	<example cmd='set host interface channel backend-0-0 interface=eth1 channel="bond0"'>
	Sets the channel for eth1 to be "bond0" (i.e., it associates eth1 with
	the bonded interface named "bond0").
	</example>

	<example cmd='set host interface channel backend-0-0 interface=eth1 channel=NULL'>
	Clear the channel entry.
	</example>
	"""

	def run(self, params, args):
		hosts = self.getHosts(args)

		(channel, interface, mac, network) = self.fillParams([
			('channel', None, True),
			('interface', None),
			('mac', None),
			('network', None)
		])

		# Gotta have one of these
		if not any([interface, mac, network]):
			raise ParamRequired(self, ('interface', 'mac', 'network'))

		# Make sure interface, mac, and/or network exist on our hosts
		self.validate(hosts, interface, mac, network)

		# Channel set to the string "NULL" is a null in the DB
		if channel.upper() == 'NULL':
			channel = None

		for host in hosts:
			if network:
				sql = """
					update networks,nodes,subnets set networks.channel=%s
					where nodes.name=%s and subnets.name=%s
					and networks.node=nodes.id and networks.subnet=subnets.id
				"""
				values = [channel, host, network]
			else:
				sql = """
					update networks,nodes set networks.channel=%s
					where nodes.name=%s and networks.node=nodes.id
				"""
				values = [channel, host]

			if interface:
				sql += " and networks.device=%s"
				values.append(interface)

			if mac:
				sql += " and networks.mac=%s"
				values.append(mac)

			self.db.execute(sql, values)

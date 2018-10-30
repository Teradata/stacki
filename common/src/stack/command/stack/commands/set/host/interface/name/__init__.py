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
from stack.exception import ParamType, ParamRequired


class Command(stack.commands.set.host.interface.command):
	"""
	Sets the logical name of a network interface on a particular host.

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

	<param type='string' name='name' optional='0'>
	Name of this interface (e.g. newname). This is only the
	name associated with a certain interface. FQDNs are disallowed.
	To set the domain or zone for an interface, use the
	"stack add network" command, and then associate the interface
	with the network
	</param>

	<example cmd='set host interface name backend-0-0 interface=eth1 name=cluster-0-0'>
	Sets the name for the eth1 device on host backend-0-0 to
	cluster-0-0.zonename. The zone is decided by the subnet that the
	interface is attached to.
	</example>
	"""

	def run(self, params, args):
		host = self.getSingleHost(args)

		(name, interface, mac, network) = self.fillParams([
			('name', None, True),
			('interface', None),
			('mac', None),
			('network', None)
		])

		# Name can't be a FQDN (IE: have dots)
		if '.' in name:
			raise ParamType(self, 'name', 'non-FQDN (base hostname)')

		# Gotta have one of these
		if not any([interface, mac, network]):
			raise ParamRequired(self, ('interface', 'mac', 'network'))

		# Make sure interface, mac, and/or network exist on our hosts
		self.validate([host], interface, mac, network)

		# If name is set to 'NULL' it gets the host name
		if name.upper() == 'NULL':
			name = host

		# Make the change in the DB
		if network:
			sql = """
				update networks,nodes,subnets set networks.name=%s
				where nodes.name=%s and subnets.name=%s
				and networks.node=nodes.id and networks.subnet=subnets.id
			"""
			values = [name, host, network]
		else:
			sql = """
				update networks,nodes set networks.name=%s
				where nodes.name=%s and networks.node=nodes.id
			"""
			values = [name, host]

		if interface:
			sql += " and networks.device=%s"
			values.append(interface)

		if mac:
			sql += " and networks.mac=%s"
			values.append(mac)

		self.db.execute(sql, values)

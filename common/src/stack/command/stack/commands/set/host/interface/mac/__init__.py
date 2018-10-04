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
	Sets the mac address for named interface on host.

	<arg type='string' name='host' optional='0'>
	A single host.
	</arg>

	<param type='string' name='interface'>
	Name of the interface.
	</param>

	<param type='string' name='mac' optional='0'>
	MAC address of the interface. Usually of the form dd:dd:dd:dd:dd:dd
	where d is a hex digit. This format is not enforced. Use mac=NULL to
	clear the mac address.
	</param>

	<param type='string' name='network'>
	Network name of the interface.
	</param>

	<example cmd='set host interface mac backend-0-0 interface=eth1 mac=00:0e:0c:a7:5d:ff'>
	Sets the MAC Address for the eth1 device on host backend-0-0.
	</example>
	"""

	def run(self, params, args):
		host = self.getSingleHost(args)

		(interface, mac, network) = self.fillParams([
			('interface', None),
			('mac', None, True),
			('network', None)
		])

		# Gotta have one of these
		if not any([interface, network]):
			raise ParamRequired(self, ('interface', 'network'))

		# Make sure mac and/or network exist on our hosts
		self.validate([host], interface, None, network)

		# If mac is an empty sting or NULL, we are clearing it
		if not mac or mac.upper() == 'NULL':
			mac = None

		# Make the change in the DB
		if network:
			sql = """
				update networks,nodes,subnets set networks.mac=%s
				where nodes.name=%s and subnets.name=%s
				and networks.node=nodes.id and networks.subnet=subnets.id
			"""
			values = [mac, host, network]
		else:
			sql = """
				update networks,nodes set networks.mac=%s
				where nodes.name=%s and networks.node=nodes.id
			"""
			values = [mac, host]

		if interface:
			sql += " and networks.device=%s"
			values.append(interface)

		self.db.execute(sql, values)

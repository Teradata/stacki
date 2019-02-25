# @copyright@
# Copyright (c) 2006 - 2019 Teradata
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
from stack.exception import ParamRequired, ParamType


class Command(stack.commands.set.host.interface.command):
	"""
	Sets the VLAN ID for an interface on one of more hosts.

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

	<param type='integer' name='vlan' optional='0'>
	The VLAN ID that should be updated. This must be an integer and the
	pair 'subnet/vlan' must be defined in the VLANs table.
	</param>

	<example cmd='set host interface vlan backend-0-0-0 interface=eth0 vlan=3'>
	Sets backend-0-0-0's private interface to VLAN ID 3.
	</example>
	"""

	def run(self, params, args):
		hosts = self.getHosts(args)

		(vlan, interface, mac, network) = self.fillParams([
			('vlan', None, True),
			('interface', None),
			('mac', None),
			('network', None)
		])

		# Gotta have one of these
		if not any([interface, mac, network]):
			raise ParamRequired(self, ('interface', 'mac', 'network'))

		# Make sure interface, mac, and/or network exist on our hosts
		self.validate(hosts, interface, mac, network)

		# vlan has to be an integer
		try:
			vlan = int(vlan)
		except:
			raise ParamType(self, 'vlan', 'integer')

		# If vlan is 0 then it should be NULL in the db
		if vlan == 0:
			vlan = None

		for host in hosts:
			if network:
				sql = """
					update networks,nodes,subnets set networks.vlanid=%s
					where nodes.name=%s and subnets.name=%s
					and networks.node=nodes.id and networks.subnet=subnets.id
				"""
				values = [vlan, host, network]
			else:
				sql = """
					update networks,nodes set networks.vlanid=%s
					where nodes.name=%s and networks.node=nodes.id
				"""
				values = [vlan, host]

			if interface:
				sql += " and networks.device=%s"
				values.append(interface)

			if mac:
				sql += " and networks.mac=%s"
				values.append(mac)

			self.db.execute(sql, values)

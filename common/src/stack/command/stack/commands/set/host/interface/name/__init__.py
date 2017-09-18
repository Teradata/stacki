# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands
from stack.exception import ParamType, ParamRequired, ArgUnique


class Command(stack.commands.set.host.command):
	"""
	Sets the logical name of a network interface on a particular host.

	<arg type='string' name='host'>
	Host name.
	</arg>
	
	<param type='string' name='interface'>
	Name of the interface.
	</param>

	<param type='string' name='mac'>
	MAC address of the interface.
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

		hosts = self.getHostnames(args)
		(name, interface, mac) = self.fillParams([
			('name',      None, True),
			('interface', None),
			('mac',       None)
			])

		if len(name.split('.')) > 1:
			raise ParamType(self, 'name', 'non-FQDN (base hostname)')
		if not interface and not mac:
			raise ParamRequired(self, ('interface', 'mac'))
		if len(hosts) != 1:
			raise ArgUnique(self, 'host')

		host = hosts[0]		

		if name.upper() == "NULL":
			name = host

		if interface:
			self.db.execute("""
				update networks, nodes set 
				networks.name='%s' where nodes.name='%s'
				and networks.node=nodes.id and
				networks.device like '%s'
				""" % (name, host, interface))
		else:
			self.db.execute("""
				update networks, nodes set 
				networks.name='%s' where nodes.name='%s'
				and networks.node=nodes.id and
				networks.mac like '%s'
				""" % (name, host, mac))


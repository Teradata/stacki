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
from stack.exception import ArgRequired, CommandError


class Command(stack.commands.set.host.command):
	"""
	Sets the mac address for named interface on host.

	<arg type='string' name='host'>
	Host name.
	</arg>

	<param type='string' name='interface' optional='0'>
	Name of the interface.
	</param>

	<param type='string' name='mac' optional='0'>
	The mac address of the interface. Usually of the form dd:dd:dd:dd:dd:dd
	where d is a hex digit. This format is not enforced. Use mac=NULL to
	clear the mac address.
	</param>

	<example cmd='set host interface mac backend-0-0 interface=eth1 mac=00:0e:0c:a7:5d:ff'>
	Sets the MAC Address for the eth1 device on host backend-0-0.
	</example>
	"""
	
	def run(self, params, args):

		(interface, mac) = self.fillParams([
			('interface', None, True),
			('mac',       None, True)
			])

		if not len(args):
			raise ArgRequired(self, 'host')

		# Prevent duplicate MACs in the cluster, but allow setting a host interface's MAC to its current value
		# (requires 'host' arg to be singular)
		host, = self.getHostnames(args)
		for iface in self.call('list.host.interface'):
			if (mac == iface['mac']
			    and (host != iface['host'] or (host == iface['host'] and interface != iface['interface']))):
				raise CommandError(self, f'MAC "{mac}" already exists on host "{iface["host"]}", interface "{iface["interface"]}"')

		self.db.execute("""
			update networks, nodes set
			networks.mac=NULLIF(%s,'NULL') where
			nodes.name=%s and networks.node=nodes.id and
			networks.device like %s
			""", (mac, host, interface))


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
from stack.exception import ParamRequired, CommandError, ArgRequired
from stack.util import flatten


class Command(stack.commands.remove.host.command):
	"""
	Remove a network interface definition for a host.

	<arg type='string' name='host' optional='1' repeat='1'>
	One or more named hosts.
	</arg>

	<param type='string' name='interface'>
	Name of the interface that should be removed.
	</param>

	<param type='string' name='mac'>
	MAC address of the interface that should be removed.
	</param>

	<param type='bool' name='all'>
	When set to true the command will remove all interfaces for the
	hosts.  This is used internally in Stacki to speed up bulk changes in
	the cluster.
	</param>

	<example cmd='remove host interface backend-0-0 interface=eth1'>
	Removes the interface eth1 on host backend-0-0.
	</example>

	<example cmd='remove host interface backend-0-0 backend-0-1 interface=eth1'>
	Removes the interface eth1 on hosts backend-0-0 and backend-0-1.
	</example>
	"""

	def run(self, params, args):
		if len(args) == 0:
			raise ArgRequired(self, 'host')

		hosts = self.getHostnames(args)
		if not hosts:
			raise ArgRequired(self, 'host')

		(interface, mac, all_interfaces) = self.fillParams([
			('interface', None),
			('mac',       None),
			('all',     'false')
		])

		all_interfaces = self.str2bool(all_interfaces)
		if not all_interfaces and not interface and not mac:
			raise ParamRequired(self, ('interface', 'mac'))

		networks = ()
		for host in hosts:
			if all_interfaces:
				networks = flatten(self.db.select("""
					id from networks where
					node=(select id from nodes where name=%s)
				""", (host,)))
			elif interface:
				networks = flatten(self.db.select("""
					id from networks where
					node=(select id from nodes where name=%s) and device=%s
				""",  (host, interface)))

				if not networks:
					raise CommandError(self, 'no interface "%s" exists on %s' % (interface, host))
			else:
				networks = flatten(self.db.select("""
					id from networks where
					node=(select id from nodes where name=%s) and mac=%s
				""", (host, mac)))

				if not networks:
					raise CommandError(self, 'no mac address "%s" exists on %s' % (mac, host))

			self.runPlugins(networks)

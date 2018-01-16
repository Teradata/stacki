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
from stack.exception import ParamRequired, CommandError


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

		(interface, mac, all) = self.fillParams([
			('interface', None),
			('mac',       None),
			('all',     'false')
			])

		all = self.str2bool(all)
		if not all and not interface and not mac:
			raise ParamRequired(self, ('interface', 'mac'))

		for host in self.getHostnames(args):
			if all:
				self.db.execute("""
					delete from networks where
					node=(select id from nodes where name='%s')
					""" %  (host))
			elif interface:
				rows_affected = self.db.execute("""
					delete from networks where
					node=(select id from nodes where name='%s')
					and device like '%s'
					""" %  (host, interface))

				if not rows_affected:
					raise CommandError(self, "No interface '%s' exists on %s." % (interface, host))
			else:
				rows_affected = self.db.execute("""
					delete from networks where
					node=(select id from nodes where name='%s')
					and mac like '%s'
					""" %  (host, mac))

				if not rows_affected:
					raise CommandError(self, "No mac address '%s' exists on %s." % (mac, host))

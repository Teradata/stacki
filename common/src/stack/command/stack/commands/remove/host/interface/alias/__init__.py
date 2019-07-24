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
from stack.exception import ArgRequired, ArgUnique, CommandError


class Command(stack.commands.remove.host.command):
	"""
	Remove an alias from a host interface.

	<arg type='string' name='host' optional='0'>
	One host.
	</arg>

	<param type='string' name='alias' optional='1'>
	The alias name that should be removed.
	</param>

	<param type='string' name='interface' optional='1'>
	Interface to remove aliases for.
	</param>

	<example cmd='remove host interface alias backend-0-0 alias=c-0-0'>
	Removes the alias "c-0-0" for host "backend-0-0".
	</example>

	<example cmd='remove host interface alias backend-0-0 interface=eth0'>
	Removes all aliases for "backend-0-0" assigned to "eth0"
	</example>

	<example cmd='remove host interface alias backend-0-0'>
	Removes all aliases for "backend-0-0".
	</example>
	"""

	def run(self, params, args):
		if len(args) == 0:
			raise ArgRequired(self, 'host')

		hosts = self.getHostnames(args)

		if not hosts:
			raise ArgRequired(self, 'host')

		if not len(hosts) == 1:
			raise ArgUnique(self, 'host')

		alias, interface, = self.fillParams([
			('alias', None),
			('interface', None)
		])

		query = """
			DELETE aliases
			FROM aliases
			LEFT JOIN networks ON aliases.network = networks.id
			LEFT JOIN nodes ON networks.node = nodes.id
			WHERE nodes.name = %s
		"""
		values = [hosts[0]]

		if alias:
			query += ' AND aliases.name = %s'
			values.append(alias)

		if interface:
			query += ' AND networks.device = %s'
			values.append(interface)

		self.db.execute(query, values)

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
import socket
from stack.exception import ArgRequired, ArgUnique, CommandError


class Command(stack.commands.add.host.command):
	"""
	Adds an alias to a host

	<arg type='string' name='host'>
	Host name of machine
	</arg>

	<param type='string' name='interface' optional='0'>
	Interface of host.
	</param>

	<param type='string' name='alias' optional='0'>
	Alias for the host.
	</param>

	<example cmd='add host alias backend-0-0 interface=eth0 alias=b00'>
	Add a host alias "b00" to host "backend-0-0" on interface "eth0".
	</example>
	"""

	def run(self, params, args):
		hosts = self.getHostnames(args)
		
		(alias, interface, ) = self.fillParams([
			('alias', None, True),
			('interface', None, True)
			])

		if not hosts:
			raise ArgRequired(self, 'host')
		if not len(hosts) == 1:
			raise ArgUnique(self, 'host')

		if alias.isdigit():
			raise CommandError(self, 'aliases cannot be only numbers')

		try:
			socket.inet_aton(alias)
			raise CommandError(self, 'aliases cannot be an IP address')
		except socket.error:
			pass

		host = hosts[0]
		for dict in self.call('list.host.alias'):
			if alias == dict['alias'] and\
			 interface == dict['device'] and\
			 hosts[0] == dict['host']:
				raise CommandError(self, 'alias "%s" exists' % alias)
			if alias == dict['alias'] and hosts[0] != dict['host']:
				raise CommandError(self, 'alias "%s" exists' % alias)

		self.db.execute("""select id from networks where
				name='%s' and device='%s'""" % (host, interface))
		if (self.db.fetchall()) == ():
			raise CommandError(self, 'Interface does not exist')

		self.db.execute("""
			insert into aliases (network, name)
			values ((select id from networks where
			name='%s' and device='%s'),'%s')
			""" % (host, interface, alias))


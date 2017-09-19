# @copyright@
# Copyright (c) 2006 - 2017 Teradata
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


class Command(stack.commands.add.host.command):
	"""
	Adds an alias to a host

	<arg type='string' name='host'>
	Host name of machine
	</arg>
	
	<param type='string' name='alias' optional='0'>
	Alias for the host.
	</param>

	<example cmd='add host alias backend-0-0 alias=b00'>
	Add a host alias "b00" to host "backend-0-0".
	</example>
	"""

	def run(self, params, args):

		hosts = self.getHostnames(args)
		
		(alias, ) = self.fillParams([
			('alias', None, True)
			])
		
		if not hosts:
			raise ArgRequired(self, 'host')
		if not len(hosts) == 1:
			raise ArgUnique(self, 'host')

		host = hosts[0]
		for dict in self.call('list.host.alias', [ 'host=%s' % host ]):
			if alias == dict['alias']:
				raise CommandError(self, 'alias "%s" exists' % alias)

		self.db.execute("""
			insert into aliases (node, name)
			values (
			(select id from nodes where name='%s'),
			'%s'
			)
			""" % (host, alias))


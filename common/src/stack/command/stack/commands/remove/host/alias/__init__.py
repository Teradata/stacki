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
from stack.exception import ArgRequired, ArgUnique, CommandError


class Command(stack.commands.remove.host.command):
	"""
	Remove an alias from a host.

	<arg type='string' name='host' optional='0'>
	One host.
	</arg>
	
	<param type='string' name='alias'>
	The alias name that should be removed.
	</param>

	<example cmd='remove host alias backend-0-0 alias=c-0-0'>
	Removes the alias "c-0-0" for host "backend-0-0".

	<example cmd='remove host alias backend-0-0 interface=eth0'>
	Removes all aliases for "backend-0-0" assigned to "eth0"
	</example>

	<example cmd='remove host alias backend-0-0'>
	Removes all aliases for "backend-0-0".
	</example>
	"""

	def run(self, params, args):

		(alias, interface, ) = self.fillParams([
			('alias', None),
			('interface', None)
			])

		hosts = self.getHostnames(args)
		if not hosts:
			raise ArgRequired(self, 'host')
		if not len(hosts) == 1:
			raise ArgUnique(self, 'host')

		for host in self.getHostnames(args):
			if not alias and not interface: 
				self.db.execute("""
					delete from aliases where 
					network IN (select id from networks where name='%s')
					""" % host)
			elif not alias:
				self.db.execute("""
					delete from aliases where 
					network IN  (select id from networks where name='%s'
					and device='%s')
					""" % (host, interface))
			elif not interface:
				self.db.execute("""
					delete from aliases where 
					network IN (select id from networks where name='%s')
					and name = '%s'
					""" % (host, alias))
			else:
				self.db.execute("""
					delete from aliases where 
					network = (select id from networks where name='%s'
					and device='%s')
					and name = '%s'
					""" % (host, interface, alias))

# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@


import stack.commands

class Command(stack.commands.remove.host.command):
	"""
	Remove an alias from a host(s).

	<arg type='string' name='host' optional='1' repeat='1'>
	One hosts.
	</arg>
	
	<param type='string' name='alias'>
	The alias name that should be removed.
	</param>

	<example cmd='remove host alias backend-0-0 alias=c-0-0'>
	Removes the alias c-0-0 for host backend-0-0.
	</example>

	<example cmd='remove host alias backend-0-0'>
	Removes all aliases for backend-0-0.
	</example>
	"""

	def run(self, params, args):
		
		(alias, ) = self.fillParams([
			('alias', None)
			])

		for host in self.getHostnames(args):
			if not alias: 
				self.db.execute("""
					delete from aliases where 
					node = (select id from nodes where name='%s')
					""" % host)
			else:
				self.db.execute("""
					delete from aliases where 
					node = (select id from nodes where name='%s')
					and name = '%s'
					""" % (host, alias))

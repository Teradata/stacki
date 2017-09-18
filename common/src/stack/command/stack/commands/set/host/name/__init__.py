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
from stack.exception import ArgUnique, CommandError


class Command(stack.commands.set.host.command):
	"""
	Rename a host.
	
	<arg type='string' name='host' repeat='0'>
	The current name of the host.
	</arg>

	<param type='string' name='name' optional='0'>
	The new name for the host.
	</param>

	<example cmd='set host name backend-0-0 name=new-backend-0-0'>
	Changes the name of backend-0-0 to new-backend-0-0.
	</example>
	"""

	def run(self, params, args):
		
		hosts = self.getHostnames(args)
		(name, ) = self.fillParams([
			('name', None, True)
			])
		
		if not len(hosts) == 1:
			raise ArgUnique(self, 'host')
		if name in self.getHostnames():
			raise CommandError(self, 'name already exists')
			
		host = hosts[0]
		
		self.db.execute("""
			update nodes set name='%s' where
			name='%s'
			""" % (name, host))
		
			


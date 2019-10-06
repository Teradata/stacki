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
from stack.exception import CommandError, ParamValue
from stack.util import is_hostname_label


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
		host = self.getSingleHost(args)

		(name, ) = self.fillParams([
			('name', None, True)
		])

		if not is_hostname_label(name):
			raise ParamValue(self, 'name', 'a valid hostname label')

		if name in self.getHostnames():
			raise CommandError(self, 'name already exists')

		self.db.execute('update nodes set name=%s where name=%s', (name, host))

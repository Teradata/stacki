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


class Command(stack.commands.list.host.command):
	"""
	Lists the aliases for a host.

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, aliases
	for all the known hosts is listed.
	</arg>

	<example cmd='list host alias backend-0-0'>
	List the aliases for backend-0-0.
	</example>
	"""

	def run(self, params, args):

		self.beginOutput()

		for host in self.getHostnames(args):
			self.db.execute("""
				select name from aliases where
				node = (select id from nodes where name='%s')
				""" % host)
			for alias, in self.db.fetchall():
				self.addOutput(host, alias)

		self.endOutput(header=['host', 'alias'], trimOwner=False)


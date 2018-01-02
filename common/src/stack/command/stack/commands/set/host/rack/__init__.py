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
from stack.exception import ArgRequired


class Command(stack.commands.set.host.command):
	"""
	Set the rack number for a list of hosts.
	
	<arg type='string' name='host' repeat='1'>
	One or more host names.
	</arg>

	<param type='string' name='rack' optional='0'>
	The rack name (usually a number) to assign to each host.
	</param>

	<example cmd='set host rack backend-2-0 rack=2'>
	Set the rack number to 2 for backend-2-0.
	</example>
	"""

	def run(self, params, args):

		(rack, ) = self.fillParams([
			('rack', None, True)
			])
		
		if not len(args):
			raise ArgRequired(self, 'host')

		for host in self.getHostnames(args):
			self.db.execute("""
				update nodes set rack='%s' where
				name='%s'
				""" % (rack, host))


# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
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
	Set the comment field for a list of hosts.
	
	<arg type='string' name='host' repeat='1'>
	One or more host names.
	</arg>

	<param type='string' name='comment' optional='0'>
	The string to assign to the comment field for each host.
	</param>

	<example cmd='set host comment backend-0-0 comment="Fast Node"'>
	Sets the comment field to "Fast Node" for backend-0-0.
	</example>
	"""

	def run(self, params, args):
		
		(comment, ) = self.fillParams([
			('comment', None, True)
			])
		
		if not len(args):
			raise ArgRequired(self, 'host')

		for host in self.getHostnames(args):
			self.db.execute("""update nodes set comment="%s" where
				name='%s'""" % (comment, host))
		

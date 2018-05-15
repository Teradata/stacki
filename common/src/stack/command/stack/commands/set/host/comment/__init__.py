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

import stack.api
import stack.commands
from stack.exception import ArgRequired, CommandError


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
		
		(comment, ) = self.fillParams([ ('comment', None, True) ])
		
		if not len(args):
			raise ArgRequired(self, 'host')

		component = stack.api.Component()
		component.set_multiple(self.getHostnames(args), comment=comment)
		

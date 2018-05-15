# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


import stack.api
import stack.commands
from stack.exception import ArgRequired

class Command(stack.commands.set.host.command):
	"""
	Sets the box for a list of hosts.
	
	<arg type='string' name='host' repeat='1'>
	One or more host names.
	</arg>

	<param type='string' name='box' optional='0'>
	The name of the box (e.g. default)
	</param>

	<example cmd='set host box backend box=default'>
	Set the box for all backend nodes to default.
	</example>
	"""

	def run(self, params, args):

		(box, ) = self.fillParams([ ('box', None, True) ])

		if not len(args):
			raise ArgRequired(self, 'host')

		host = stack.api.Host()
		host.set_multiple(self.getHostnames(args), box=box)



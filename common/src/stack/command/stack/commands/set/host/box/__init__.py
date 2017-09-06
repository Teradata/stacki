# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

import os
import stack.commands
from stack.exception import *

class Command(stack.commands.set.host.command,
	      stack.commands.BoxArgumentProcessor):
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
		if not len(args):
			raise ArgRequired(self, 'host')

		box, = self.fillParams([ ('box', None, True) ])
		
		# Check to make sure this is a valid box name

		self.getBoxNames([ box ])

		for host in self.getHostnames(args):
			self.db.execute("""update nodes set box=
				(select id from boxes where name='%s')
				where name='%s' """
				% (box, host))

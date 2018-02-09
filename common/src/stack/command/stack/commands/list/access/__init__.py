# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import grp
import stack.commands


class Command(stack.commands.list.command):
	"""
	List the Access control for RCL commands

	<example cmd='list access'>
	List the Access control for RCL commands
	</example>
	"""		

	def run(self, params, args):

		self.beginOutput()
		
		for (cmd, gid) in self.db.select("""
			command, groupid from access
			"""):
			try:
				group = grp.getgrgid(gid).gr_name
			except:
				group = gid
			self.addOutput(cmd, (group))
			
		self.endOutput(header=['command', 'group'], trimOwner=False)
		

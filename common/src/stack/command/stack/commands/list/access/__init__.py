# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

import grp
import stack.commands


class Command(stack.commands.list.command):
	"""
	List the Access control for RCL commands
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
		

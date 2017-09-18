# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import grp
import stack.commands
from stack.exception import CommandError


class Command(stack.commands.set.command):
	"""
	Sets an Access control pattern.
	
	<param name="command" optional='0'>
	Command Pattern.
	</param>
	
	<param name="group" optional='0'>
	Group name / ID for access.
	</param>
	
	<example cmd='set access command="*" group=apache'>
	Give "apache" group access to all "stack" commands
	</example>
	
	<example cmd='set access command="list*" group=wheel'>
	Give "wheel" group access to all "stack list" commands
	</example>
	"""

	def run(self, params, args):

		
		(cmd, group) = self.fillParams([
			('command', None, True),
			('group',   None, True)
			])
		 
		groupid = None
		try:
			groupid = int(group)
		except ValueError:
			pass

		if groupid is None:
			try:
				groupid = grp.getgrnam(group).gr_gid
			except KeyError:
				raise CommandError(self, 'cannot find group %s' % group)

		if groupid is None:
			raise CommandError(self, 'cannot find group %s' % group)

		self.db.execute("""
			insert into access (command, groupid)
			values ('%s', %d)
			""" % (cmd, groupid))

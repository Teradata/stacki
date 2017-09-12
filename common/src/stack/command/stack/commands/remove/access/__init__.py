# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

import grp
import stack.commands
from stack.exception import CommandError


class Command(stack.commands.Command):
	"""
	Remove Access control pattern.
	
	<param name="command" optional='0'>
	Command Pattern.
	</param>
	
	<param name="group" optional='0'>
	Group name / ID for access.
	</param>
	
	<example cmd='remove access command="*" group=apache'>
	Remove "apache" group access to all "rocks" commands
	</example>
	
	<example cmd='remove access command="list*" group=wheel'>
	Remove "wheel" group access to all "rocks list" commands
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

		self.db.execute("""delete from access where
			command="%s" and groupid=%d""" 
			% (cmd, groupid))

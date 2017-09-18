# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgRequired, ArgUnique, CommandError


class Command(stack.commands.remove.command):
	"""
	Removes a Group.

	Groups are generic sets of hosts, they have no semantics other
	than enforcing a common group membership. Hosts may belong to
	zero or more groups, and by default belong to none.

	Only groups without member hosts can be removed.
	
	<arg type='string' name='group'>
	The name of the group to be removed.
	</arg>

	"""		

	def run(self, params, args):
		if not len(args):
			raise ArgRequired(self, 'group')
		if len(args) > 1:
			raise ArgUnique(self, 'group')

		group = args[0]

		hosts = None
		for row in self.call('list.group'):
			if group == row['group']:
				hosts = row['hosts']
				break
		if hosts is None:
			raise CommandError(self, 'group %s does not exist' % group)
		if len(hosts) > 0:
			raise CommandError(self, 'group %s is in use' % group)
		
		self.db.execute(
			"""
			delete from groups
			where
			name = '%s'
			""" % group)


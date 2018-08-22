# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgRequired, ArgUnique, CommandError


class Command(stack.commands.add.command):
	"""
	Adds Group.

	Groups are generic sets of hosts, they have no semantics other
	than enforcing a common group membership. Hosts may belong to
	zero or more groups, and by default belong to none.
	
	<arg type='string' name='group'>
	The name of the group to be created.
	</arg>

	"""		

	def run(self, params, args):
		if not len(args):
			raise ArgRequired(self, 'group')
		if len(args) > 1:
			raise ArgUnique(self, 'group')

		group = args[0]

		if self.db.select(
			'count(ID) from groups where name=%s',
			(group,)
		)[0][0] > 0:
			raise CommandError(self, '"%s" group already exists' % group)

		self.db.execute(
			'insert into groups(name) values (%s)',
			(group,)
		)

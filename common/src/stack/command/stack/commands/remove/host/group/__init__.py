# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


import stack.commands
from stack.exception import ArgRequired, ArgUnique, CommandError


class Command(stack.commands.remove.host.command):
	"""
	Removes a group from one or more hosts.

	<arg type='string' name='host' repeat='1'>
	One or more host names.
	</arg>

	<param type='string' name='group' optional='0'>
	Group for the host.
	</param>

	<example cmd='remove host group backend-0-0 group=test'>
	Removes host backend-0-0 from the test group.
	</example>
	"""

	def run(self, params, args):
		if len(args) == 0:
			raise ArgRequired(self, 'host')

		hosts = self.getHostnames(args)
		if not hosts:
			raise ArgRequired(self, 'host')

		(group, ) = self.fillParams([
			('group', None, True)
		])

		membership = {
			row['host']: row['groups'] for row in self.call('list.host.group')
		}

		for host in hosts:
			if group not in membership[host]:
				raise CommandError(self, '%s is not a member of %s' % (host, group))

		for host in hosts:
			self.db.execute("""
				delete from memberships
				where nodeid=(select id from nodes where name=%s)
				and	groupid=(select id from groups where name=%s)
			""", (host, group))

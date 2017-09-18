# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgRequired, CommandError


class Command(stack.commands.add.host.command):
	"""
	Adds a group to one or more hosts.

	<arg type='string' name='host' repeat='1'>
	One or more host names.
	</arg>

	<param type='string' name='group' optional='0'>
	Group for the host.
	</param>

	<example cmd='add host group backend-0-0 group=test'>
	Adds host backend-0-0 to the test group.
	</example>
	"""

	def run(self, params, args):

		if len(args) == 0:
			raise ArgRequired(self, 'host')
	
		hosts = self.getHostnames(args)
		
		(group, ) = self.fillParams([
			('group', None, True)
			])
		
		if not hosts:
			raise ArgRequired(self, 'host')

		exists = False
		for row in self.call('list.group'):
			if group == row['group']:
				exists = True
				break
		if not exists:
			raise CommandError(self, 'group %s does not exist' % group)
			
		membership  = {}
		for row in self.call('list.host.group'):
			membership[row['host']] = row['groups']


		for host in hosts:
			if group in membership[host]:
				raise CommandError(self, '%s already member of %s' % (host, group))

		for host in hosts:
			self.db.execute(
				"""
				insert into memberships 
				(nodeid, groupid)
				values (
				(select id from nodes where name='%s'),
				(select id from groups where name='%s'))
				""" % (host, group))
		


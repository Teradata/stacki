# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands
from stack.exception import ArgRequired, CommandError


class Command(stack.commands.set.host.command):
	"""
	Set the run action for a list of hosts.
	
	<arg type='string' name='host' repeat='1'>
	One or more host names.
	</arg>

	<param type='string' name='action' optional='0'>
	The run action to assign to each host. To get a list of all actions,
	execute: "stack list bootaction".
	</param>

	<example cmd='set host osaction backend-0-0 action=os'>
	Sets the run action to "os" for backend-0-0.
	</example>

	<example cmd='set host osaction backend-0-0 backend-0-1 action=memtest'>
	Sets the run action to "memtest" for backend-0-0 and backend-0-1.
	</example>
	"""

	def run(self, params, args):

		(action, ) = self.fillParams([
			('action', None, True)
			])
		
		if not len(args):
			raise ArgRequired(self, 'host')

		if action.lower() == 'none':
			runaction = 'NULL'
		else:
			rows = self.db.execute(
				"""
				select ba.bootname from 
				bootactions ba, bootnames bn 
				where bn.name='%s' 
				and ba.bootname=bn.id
				and bn.type = 'os';
				""" % (action))

			if rows != 1:
				raise CommandError(self, 'invalid action parameter')
			# OSaction is now an ID, not a name so fetch it.
			osaction, = self.db.fetchone()

		for host in self.getHostnames(args):
			self.db.execute("""
				update nodes set osaction=%s
				where name='%s'
				""" % (osaction, host))


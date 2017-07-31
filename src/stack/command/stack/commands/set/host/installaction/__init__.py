# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@

import stack.commands
from stack.exception import *

class Command(stack.commands.set.host.command):
	"""
	Set the install action for a list of hosts.
	
	<arg type='string' name='host' repeat='1'>
	One or more host names.
	</arg>

	<param type='string' name='action' optional='0'>
	The install action to assign to each host. To get a list of all actions,
	execute: "stack list bootaction".
	</param>

	<example cmd='set host installaction backend-0-0 action=install'>
	Sets the install action to "install" for backend-0-0.
	</example>

	<example cmd='set host installaction backend-0-0 backend-0-1 action="install i386"'>
	Sets the install action to "install i386" for backend-0-0 and backend-0-1.
	</example>
	"""

	def run(self, params, args):

		(action, ) = self.fillParams([
			('action', None, True)
			])
		
		if not len(args):
			raise ArgRequired(self, 'host')

		if action.lower() == 'none':
			installaction = 'NULL'
		else:
			rows = self.db.execute("""
				select ba.bootname from 
				bootactions ba, bootnames bn 
				where bn.name='%s' 
				and ba.bootname=bn.id
				and bn.type = 'install';
				""" % (action))
			if rows != 1:
				nrows = self.db.execute("""
				select name from bootnames 
				where type="install";
				""")
				actions = self.db.fetchall()
				msg = '\n\nThese are the available actions: \n' 
				msg += '\n'.join([ a[0] for a in actions])
				raise CommandError(self, 'invalid action parameter' + msg)
			
			installaction, = self.db.fetchone()
			
		for host in self.getHostnames(args):
			self.db.execute("""
				update nodes set installaction=%s
				where name='%s'
				""" % (installaction, host))

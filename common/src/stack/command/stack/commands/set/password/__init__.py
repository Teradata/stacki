# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import os
import pwd
import getpass
import stack.commands
from stack.exception import CommandError


class Command(stack.commands.Command):
	"""
	Change the root password for relevant cluster services.  In particular, this changes the Unix
	'root' account password for the Frontend.  Note that this password is also the default
	password for all backend nodes, but backends will not have their passwords set to the new
	password until after a reinstall.

	<example cmd='set password'>
	Set the password for Stacki.  You will be prompted for the current password and the new password.
	</example>
	"""
	
	def run(self, params, args):
		
		if len(args):
			raise CommandError(self, 'command does not take arguments')

		p = pwd.getpwuid(os.geteuid())
		if p[0] != 'root':
			raise CommandError(self, 'must be root (or have root privileges) to run this command')

		# note that plugin_unix does not care what the current password is, but other plugins could...
		old_password = getpass.getpass('current system password: ')

		while 1:
			new_password = getpass.getpass('new system password: ')
			confirm_new_password = getpass.getpass(
				'retype new system password: ')

			if new_password == confirm_new_password:
				break
			else:
				print('Sorry, the passwords do not match')
		
		self.runPlugins( [ old_password, new_password ] )


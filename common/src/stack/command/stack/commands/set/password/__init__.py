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

import os
import pwd
import getpass
import stack.commands
from stack.exception import CommandError


class Command(stack.commands.Command):
	"""
	Change the root password for relevant cluster services.
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


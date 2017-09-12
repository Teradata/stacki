# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

import stack.commands
from stack.exception import ArgRequired, ArgUnique, CommandError


class command(stack.commands.EnvironmentArgumentProcessor,
	      stack.commands.add.command):
	pass


class Command(command):
	"""
	Add an environment to the database.
	
	<arg type='string' name='environment'>
	The environment name.
	</arg>
	"""

	def run(self, params, args):

		if len(args) == 0:
			raise ArgRequired(self, 'environment')
		if len(args) != 1:
			raise ArgUnique(self, 'environment')
		environment = args[0]

		dup = False
		for row in self.db.select(
			"""
			* from environments where name='%s'
			""" % environment):
			dup = True
		if dup:
			raise CommandError(self, 'environment "%s" already exists' % environment)

		self.db.execute(
			"""
			insert into environments (name) values ('%s')
			""" % environment)
		

# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.commands import EnvironmentArgProcessor
from stack.exception import ArgRequired, ArgUnique, CommandError


class command(EnvironmentArgProcessor, stack.commands.add.command):
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

		if self.db.count(
			'(ID) from environments where name=%s',
			(environment,)
		) > 0:
			raise CommandError(self, 'environment "%s" already exists' % environment)

		self.db.execute(
			'insert into environments(name) values (%s)',
			(environment,)
		)

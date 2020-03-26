# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.commands import EnvironmentArgProcessor
from stack.exception import ArgRequired, CommandError

class command(EnvironmentArgProcessor, stack.commands.remove.command):
	pass


class Command(command):
	"""
	Remove an Envirornment.  If the environment is currently
	being used (has attributes, or hosts) an error is raised.

	<arg type='string' name='environment' repeat='1'>
	One or more Environment specifications (e.g., 'test').
	</arg>
	"""

	def run(self, params, args):
		if len(args) < 1:
			raise ArgRequired(self, 'environment')

		enviroments = self.getEnvironmentNames(args)

		# Figure out if any of the environments are in use
		in_use = {host['environment'] for host in self.call('list.host')}
		for environment in enviroments:
			if environment in in_use:
				raise CommandError(self, 'environment %s in use' % environment)

		# Free to remove them
		for environment in enviroments:
			self.db.execute('delete from environments where name=%s', (environment,))

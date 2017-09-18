# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgRequired, CommandError


class command(stack.commands.EnvironmentArgumentProcessor,
	      stack.commands.remove.command):
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

		active = {}
		for row in self.call('list.host'):
			active[row['environment']] = True
		for row in self.call('list.environment.attr'):
			active[row['environment']] = True
			
		if not args:
			raise ArgRequired(self, 'environment')

		for env in self.getEnvironmentNames(args):
			if env in active:
				raise CommandError(self, 'environment %s in use' % env)
			self.db.execute('delete from environments where name="%s"' % env)




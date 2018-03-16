# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgRequired, CommandError


class Command(stack.commands.EnvironmentArgumentProcessor,
	      stack.commands.set.host.command):
	"""
	Specifies an Environment for the gives hosts.  Environments are
	used to add another level to attribute resolution.  This is commonly
	used to partition a single Frontend into managing multiple clusters.
	
	<arg type='string' name='host' repeat='1'>
	One or more host names.
	</arg>

	<param type='string' name='environment' optional='0'>
	The environment name to assign to each host.
	</param>

	<example cmd='set host environment backend environment=test'>
	Assign all backend appliance host to the test environment.
	</example>
	"""

	def run(self, params, args):

		(environment, ) = self.fillParams([
			('environment', None, True)
			])

		print('set host environment', environment)
		
		if not len(args):
			raise ArgRequired(self, 'host')

		if environment and environment not in self.getEnvironmentNames():
			raise CommandError(self, 'environment parameter not valid')

		for host in self.getHostnames(args):
			self.db.execute("""
				update nodes set environment=
				(select id from environments where name='%s')
				where name='%s'
				""" % (environment, host))


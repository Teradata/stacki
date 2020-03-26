# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.commands import EnvironmentArgProcessor
from stack.exception import CommandError


class Command(EnvironmentArgProcessor, stack.commands.set.host.command):
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
		hosts = self.getHosts(args)

		(environment, ) = self.fillParams([
			('environment', None, True)
		])

		if environment not in self.getEnvironmentNames():
			raise CommandError(self, 'environment parameter not valid')

		for host in hosts:
			self.db.execute("""
				update nodes set environment=(
					select id from environments where name=%s
				) where name=%s
			""", (environment, host))

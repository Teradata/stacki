# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.commands import HostArgProcessor
from stack.exception import ArgUnique


class Command(HostArgProcessor, stack.commands.report.command):
	"""
	Output the storage controller configuration for a specific host

	<arg type='string' name='host'>
	One host name.
	</arg>

	<example cmd='report host storage controller backend-0-0'>
	Output the storage controller configuration for backend-0-0.
	</example>
	"""

	def run(self, params, args):
		hosts = self.getHostnames(args)

		if len(hosts) != 1:
			raise ArgUnique(self, 'host')

		self.beginOutput()
		self.addOutput('', str(
			self.call('list.host.storage.controller', [hosts[0]])
		))
		self.endOutput(padChar='')

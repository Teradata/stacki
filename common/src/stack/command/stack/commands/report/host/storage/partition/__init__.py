# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgUnique


class Command(stack.commands.HostArgumentProcessor, stack.commands.report.command):
	"""
	Output the storage partition configuration for a specific host

	<arg type='string' name='host'>
	One host name.
	</arg>

	<example cmd='report host storage partition backend-0-0'>
	Output the storage partition configuration for backend-0-0.
	</example>
	"""

	def run(self, params, args):
		hosts = self.getHostnames(args)

		if len(hosts) != 1:
			raise ArgUnique(self, 'host')

		self.beginOutput()

		# Get the partitions, removing 'source' to keep the existing output structure
		partitions = self.call('list.host.storage.partition', [hosts[0]])
		for partition in partitions:
			partition.pop('source', None)

		self.addOutput('', str(partitions))
		self.endOutput(padChar='')

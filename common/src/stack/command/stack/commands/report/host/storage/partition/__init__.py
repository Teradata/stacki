# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgUnique


class Command(stack.commands.HostArgumentProcessor,
	stack.commands.report.command):
	"""
	Output the storage partition configuration for a specific host

	<arg type='string' name='host'>
	One host name.
	</arg>

	<example cmd='report host storage partition compute-0-0'>
	Output the storage partition configuration for compute-0-0.
	</example>
	"""

	def run(self, params, args):
		hosts = self.getHostnames(args)

		self.beginOutput()

		if len(hosts) == 0:
			output = []
			self.addOutput('', '%s' % output)
			self.endOutput(padChar='')
			return
		elif len(hosts) > 1:
			raise ArgUnique(self, 'host')

		host = hosts[0]

		#
		# first see if there is a storage partition configuration for
		# this specific host
		#
		output = self.call('list.storage.partition', [ host ])
		if output:
			self.addOutput('', '%s' % output)
			self.endOutput(padChar='')
			return

		# 
		# now check at the appliance level
		# 
		appliance = self.getHostAttr(host, 'appliance')

		output = self.call('list.storage.partition', [ appliance ])
		if output:
			self.addOutput('', '%s' % output)
			self.endOutput(padChar='')
			return

		#
		# finally check the global level
		#
		output = self.call('list.storage.partition', ['globalOnly=y'])
		if output:
			self.addOutput('', '%s' % output)
			self.endOutput(padChar='')
			return

		#
		# if we made it here, there is no storage partition
		# configuration for this host
		#
		output = []
		self.addOutput('', '%s' % output)
		self.endOutput(padChar='')

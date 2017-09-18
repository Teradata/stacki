# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
# 

import stack.commands
from stack.exception import ArgUnique


class Command(stack.commands.HostArgumentProcessor,
	stack.commands.report.command):
	"""
	Output the storage controller configuration for a specific host

	<arg type='string' name='host'>
	One host name.
	</arg>

	<example cmd='report host storage controller compute-0-0'>
	Output the storage controller configuration for compute-0-0.
	</example>
	"""

	def run(self, params, args):
		hosts = self.getHostnames(args)

		if len(hosts) != 1:
			raise ArgUnique(self, 'host')

		self.beginOutput()

		host = hosts[0]

		#
		# first see if there is a storage controller configuration for
		# this specific host
		#
		output = self.call('list.storage.controller', [ host ])
		if output:
			self.addOutput('', '%s' % output)
			self.endOutput(padChar='')
			return

		# 
		# now check at the appliance level
		# 
		appliance = self.getHostAttr(host, 'appliance')

		output = self.call('list.storage.controller', [ appliance ])
		if output:
			self.addOutput('', '%s' % output)
			self.endOutput(padChar='')
			return

		#
		# finally check the global level
		#
		output = self.call('list.storage.controller')
		if output:
			self.addOutput('', '%s' % output)
			self.endOutput(padChar='')
			return

		#
		# if we made it here, there is no storage controller
		# configuration for this host
		#
		output = []
		self.addOutput('', '%s' % output)
		self.endOutput(padChar='')

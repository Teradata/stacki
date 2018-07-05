# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgUnique


class Command(stack.commands.HostArgumentProcessor,
              stack.commands.OSArgumentProcessor,
              stack.commands.ApplianceArgumentProcessor,
              stack.commands.EnvironmentArgumentProcessor,
              stack.commands.report.command):
	"""
	Output the storage partition configuration for a specific host

	<arg type='string' name='host'>
	One host name.
	</arg>

	<example cmd='report host storage partition backend-0-0'>
	Output the storage partition configuration for backend-0-0.
	</example>
	"""

	def list_partition_scope(self, scope=[]):
		output = self.call('list.storage.partition', scope)
		if output:
			self.addOutput('', '%s' % output)
			self.endOutput(padChar='')
		return output


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

		# host level gets first priority, then environment, appliance, os, and last global scope.
		for each_scope in ['host', 'environment', 'appliance', 'os', 'global']:
			# Setup the input for each scope correctly:
			if each_scope == 'host':
				# first see if there is a storage partition configuration for this specific host
				current_scope = [host, 'scope=%s' % each_scope]
			elif each_scope != 'global':
				# next check the attribute for environment, appliance, then os
				current_scope = [self.getHostAttr(host, each_scope), 'scope=%s' % each_scope]
				if current_scope[0] is None:
					continue
			else:
				# finally check the global level
				current_scope = ['globalOnly=y']

			output = self.list_partition_scope(current_scope)
			if output:
				# break out of here if we got output
				break

		# Default to empty list if we can't find anything.
		if not output:
			output = []
			self.addOutput('', '%s' % output)
			self.endOutput(padChar='')

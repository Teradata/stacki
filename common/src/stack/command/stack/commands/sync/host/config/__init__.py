# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

import sys
import stack.commands
import stack.util

class Command(stack.commands.sync.host.command,
	stack.commands.HostArgumentProcessor):
	"""
	!!! Rocks+ Internal Only !!!
	Generate host specific configuration files
	on the frontend
	<arg name="hostname" type="string" repeat="1">
	Hostname(s)
	</arg>
	"""
	def run(self, params, args):

		self.notify('Sync Host Config\n')

		hosts = self.getHostnames(args)
		attrs = {}

		for host in self.getHostnames(args):
			attrs[host] = {}
		for row in self.call('list.host.attr', hosts):
			attrs[row['host']][row['attr']] = row['value']

		self.runPlugins({ 'hosts': hosts,
				  'attrs': attrs })

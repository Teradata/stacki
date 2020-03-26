# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import stack.util


class Command(stack.commands.sync.host.command):
	"""
	!!! Rocks+ Internal Only !!!
	Generate host specific configuration files
	on the frontend
	<arg name="hostname" type="string" repeat="1">
	Hostname(s)
	</arg>
	"""
	def run(self, params, args):

		self.notify('Sync Host Config')

		hosts = self.getHostnames(args)
		attrs = {}

		for host in self.getHostnames(args):
			attrs[host] = {}
		for row in self.call('list.host.attr', hosts):
			attrs[row['host']][row['attr']] = row['value']

		self.runPlugins({ 'hosts': hosts,
				  'attrs': attrs })

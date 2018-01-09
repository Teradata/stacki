# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import stack.util

class command(stack.commands.HostArgumentProcessor,
	stack.commands.list.command):
	pass

class Command(command):
	"""
	"""
	def run(self, params, args):
		
		(order, ) = self.fillParams([ ('order', 'asc') ])
				
		hosts = self.getHostnames(args, order=order)

		header = ['host']
		values = {}
		for host in hosts:
			values[host] = []

		for (provides, result) in self.runPlugins(hosts):
			header.extend(result['keys'])
			for h, v in result['values'].items():
				values[h].extend(v)

		self.beginOutput()
		for host in hosts:
			if values[host]:
				self.addOutput(host, values[host])
		self.endOutput(header=header, trimOwner=False)


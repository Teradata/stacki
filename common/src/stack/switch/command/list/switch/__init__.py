# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import stack.util

class command(stack.commands.SwitchArgumentProcessor,
	stack.commands.list.command):
	pass

class Command(command):
	"""
	"""
	def run(self, params, args):
		
		(order, ) = self.fillParams([ ('order', 'asc') ])
				
		switches = self.getSwitchNames(args)

		header = ['switch']
		values = {}
		for switch in switches:
			values[switch] = []

		for (provides, result) in self.runPlugins(switches):
			header.extend(result['keys'])
			for h, v in result['values'].items():
				values[h].extend(v)

		self.beginOutput()
		for switch in switches:
			if values[switch]:
				self.addOutput(switch, values[switch])
		self.endOutput(header=header, trimOwner=False)


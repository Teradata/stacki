# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands


class command(stack.commands.SwitchArgumentProcessor,
	stack.commands.list.command):
	pass
	

class Command(command):
	"""
	"""
	def run(self, params, args):
	    
		hosts = self.getSwitchNames(args)
	    
		header = []
		values = {}
			
		for (provides, result) in self.runPlugins(hosts):
			header.extend(result['keys'])
			for h, v in result['values'].items():
				values[h] = v

		self.beginOutput()
		for host in values:
			self.addOutput(host, values[host])
		self.endOutput(header=header, trimOwner=False)


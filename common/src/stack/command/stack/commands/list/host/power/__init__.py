# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgRequired, ParamError


class Command(stack.commands.list.host.command):
	"""
	Sends a "power status" command to a host.
	
	<arg type='string' name='host' repeat='1'>
	One or more host names.
	</arg>

	<example cmd='list host power stacki-1-1'>
	Lists the current power setting for host stacki-1-1.
	</example>
	"""

	def run(self, params, args):
		if not len(args):
			raise ArgRequired(self, 'host')

		self.beginOutput()
		
		for host in self.getHostnames(args):
			status = None
			output = self.call('set.host.power', [ host, 'command=status' ])
			for o in output:
				line = o['col-1']
				if line.startswith('Chassis Power is'):
					l = line.split()
					if len(l) == 4:
						status = l[3].strip()
			self.addOutput(host, (status,))

		self.endOutput(header=['host', 'power'], trimOwner=False)

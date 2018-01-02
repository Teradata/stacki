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


import stack
import stack.commands


class Command(stack.commands.HostArgumentProcessor,
	stack.commands.report.command):
	"""
	Output the kernel boot flags for a specific host

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, info about
	all the known hosts is listed.
	</arg>

	<example cmd='report host bootflags backend-0-0'>
	Output the kernel boot flags for backend-0-0.
	</example>
	"""

	def run(self, params, args):
		self.beginOutput()

		hosts = self.getHostnames(args)
		for host in hosts:
			flags = self.getHostAttr(host, 'bootflags')
			if not flags:
				flags = ''
			self.addOutput(host, '%s' % flags)
			
		self.endOutput(padChar='', trimOwner=True)


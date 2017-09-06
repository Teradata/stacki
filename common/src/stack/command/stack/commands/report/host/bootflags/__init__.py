# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@


import os
import sys
import stack
import string
import stack.commands

class Command(stack.commands.HostArgumentProcessor,
	stack.commands.report.command):
	"""
	Output the kernel boot flags for a specific host

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, info about
	all the known hosts is listed.
	</arg>

	<example cmd='report host bootflags compute-0-0'>
	Output the kernel boot flags for compute-0-0.
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


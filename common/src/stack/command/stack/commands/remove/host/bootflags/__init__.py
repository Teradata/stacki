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

import stack.commands


class Command(stack.commands.remove.host.command):
	"""
	Remove the kernel boot flags for a list of hosts.

	<arg type='string' name='host' repeat='1'>
	List of hosts to remove kernel boot flag definitions. If no hosts are
	listed, then the global definition is removed.
	</arg>

	<example cmd='remove host bootflags backend-0-0'>
	Remove the kernel boot flags definition for backend-0-0.
	</example>
	"""

	def run(self, params, args):
		# If no host list is provided remove the default (global) boot
		# flags. Otherwise remove the flags for each supplied host.
		
		if len(args) == 0:
			self.command('remove.attr', [ 'attr=bootflags' ])
		else:
			for host in self.getHostnames(args):
				self.command('remove.host.attr', [ host,
					'attr=bootflags' ])


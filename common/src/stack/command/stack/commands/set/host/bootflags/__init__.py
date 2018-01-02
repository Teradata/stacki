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


class Command(stack.commands.set.host.command):
	"""
	Set the boot flags for a host. The boot flags will applied to the
	configuration file that a host uses to boot the running kernel. For
	example, if a node uses GRUB as its boot loader, the boot flags will 
	part of the 'append' line.
	
	<arg type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, then the
	global bootflag will be set.
	</arg>

	<param type='string' name='flags'>
	The boot flags to set for the host.
	</param>
		
	<example cmd='set host bootflags backend-0-0 flags="mem=1024M"'>
	Apply the kernel boot flags "mem=1024M" to backend-0-0.
	</example>
	"""

	def run(self, params, args):
		if len(args) == 0:
			hosts = []
		else:
			hosts = self.getHostnames(args)

		(flags, ) = self.fillParams( [('flags', None, True)] )
			
		if not hosts:
			#
			# set the global configuration
			#
			self.command('set.attr', [ 'attr=bootflags', 
				'value="%s"' % flags ])
		else:
			for host in hosts:
				self.command('set.host.attr', [ host,
					'attr=bootflags',
					'value="%s"' % flags ])


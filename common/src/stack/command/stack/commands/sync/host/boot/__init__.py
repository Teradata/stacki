# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Command(stack.commands.sync.host.command):
	"""
	You'll rarely have to use this command.

	It usually gets run as part of the 
	"stack set host boot" command.

	Recreates the /tftpboot/pxelinux/pxelinux.cfg/
	pxe boot files for backend nodes.

	If the "stack set host boot &lt;nodes&gt; action=install"
	these will install from the network.

	If the "stack set host boot &lt;nodes&gt; action=os"
	backends install from local disk.

	<example cmd='sync host bootfile'> 
	Rebuild all tftpboot files for backend nodes.
	</example>
	"""
	def run(self, params, args):

		self.notify('Sync Host Boot\n')

		argv = self.getHostnames(args, managed_only=True)
		argv.append('notify=true')
		self.report('report.host.bootfile', argv)

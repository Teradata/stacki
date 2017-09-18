#
# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
#

import stack.commands


class Command(stack.commands.HostArgumentProcessor,
	stack.commands.BoxArgumentProcessor, stack.commands.report.command):
	"""
	Create a report that describes the repository configuration file
	that should be put on hosts.

	<arg optional='0' type='string' name='host'>
	Host name of machine
	</arg>
	
	<example cmd='report host repo compute-0-0'>
	Create a report of the repository configuration file for compute-0-0.
	</example>
	"""

	def run(self, params, args):

		self.beginOutput()

		hosts = self.getHostnames(args)
		for host in hosts:
			osname = self.db.getHostOS(host)
			server = self.getHostAttr(host, 'Kickstart_PrivateAddress')
			
			if osname in [ 'redhat', 'sles' ]:
				self.runImplementation('repo', (host, server, osname))
			else:
				self.runImplementation(osname, (host, server))

		self.endOutput(padChar='', trimOwner=True)



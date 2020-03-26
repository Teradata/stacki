#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
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
from stack.commands import BoxArgProcessor, HostArgProcessor

class Command(BoxArgProcessor, HostArgProcessor, stack.commands.report.command):
	"""
	Create a report that describes the repository configuration file
	that should be put on hosts.

	<arg optional='0' type='string' name='host'>
	Host name of machine
	</arg>

	<example cmd='report host repo backend-0-0'>
	Create a report of the repository configuration file for backend-0-0.
	</example>
	"""

	def run(self, params, args):

		self.beginOutput()

		hosts = self.getHostnames(args)
		for host in hosts:
			osname = self.db.getHostOS(host)
			server = self.getHostAttr(host, 'Kickstart_PrivateAddress')

			self.runImplementation(osname, (host, server))

		self.endOutput(padChar='', trimOwner=True)



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


import stack.commands
from stack.commands import HostArgProcessor

class Command(HostArgProcessor, stack.commands.report.command):
	"""
	Create a report that contains the static routes for a host.
 
	<arg optional='0' type='string' name='host'>
	Host name of machine
	</arg>

	<example cmd='report host route backend-0-0'>
	Create a report of the static routes assigned to backend-0-0.
	</example>
	"""

	def run(self, params, args):
		self.beginOutput()

		hosts = self.getHostnames(args)
		for host in hosts:
			osname = self.db.getHostOS(host)
			self.runImplementation(osname, [host])
		self.endOutput(padChar='', trimOwner=True)


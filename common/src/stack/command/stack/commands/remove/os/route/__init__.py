# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands
from stack.exception import ArgRequired


class Command(stack.commands.remove.os.command):
	"""
	Remove a static route for an OS type.

	<arg type='string' name='os' repeat='1'>
	The OS type (e.g., 'linux', 'sunos', etc.).
	</arg>

	<param type='string' name='address' optional='0'>
	The address of the static route to remove.
	</param>

	<example cmd='remove os route linux address=1.2.3.4'>
	Remove the static route for the OS 'linux' that has the
	network address '1.2.3.4'.
	</example>
	"""

	def run(self, params, args):

		(address, ) = self.fillParams([ ('address', None, True) ])

		if len(args) == 0:
			raise ArgRequired(self, 'os')

		for os in self.getOSNames(args):
			self.db.execute("""delete from os_routes where 
			os = '%s' and network = '%s'""" % (os, address))


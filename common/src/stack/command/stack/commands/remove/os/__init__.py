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
from stack.commands import OSArgProcessor
from stack.exception import ArgRequired


class command(OSArgProcessor, stack.commands.remove.command):
	pass


class Command(command):
	"""
	Remove an OS definition from the system.

	<arg type='string' name='os' repeat='1'>
	The OS type (e.g., "linux", "sunos").
	</arg>

	<example cmd='remove os sunos'>
	Removes the OS type "sunos" from the database.
	</example>
	"""

	def run(self, params, args):

		if len(args) < 1:
			raise ArgRequired(self, 'os')

		for os in self.getOSNames(args):
			self.db.execute('delete from oses where name=%s', (os,))

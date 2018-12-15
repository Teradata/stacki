# @copyright@
# Copyright (c) 2006 - 2018 Teradata
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
from stack.exception import ArgRequired, CommandError


class Command(stack.commands.add.firmware.command):
	"""
	Adds a firmware make to the stacki database.

	<arg type='string' name='make' repeat='1'>
	One or more make names to add. Make names are required to be unique, and any duplicates will be ignored.
	</arg>

	<example cmd="add firmware make chevrolet mercedes">
	Adds two makes with the names 'chevrolet' and 'mercedes' to the set of available firmware makes.
	</example>
	"""

	def run(self, params, args):
		# Require at least one make name
		if not args:
			raise ArgRequired(self, 'make')

		# get rid of any duplicate names
		makes = set(args)
		# ensure the make name doesn't already exist
		for make in makes:
			if self.db.count('(id) FROM firmware_make WHERE name=%s', make) > 0:
				raise CommandError(cmd = self, msg = f'Firmware make with name {make} already exists.')

		self.runPlugins(args = makes)

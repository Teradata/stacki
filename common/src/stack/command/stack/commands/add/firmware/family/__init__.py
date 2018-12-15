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
	Adds a firmware family to the stacki database.

	<arg type='string' name='family' repeat='1'>
	One or more family names to add. Family names are required to be unique, and any duplicates will be ignored.
	</arg>

	<example cmd="add firmware family my_awesome_family my_less_awesome_inlaws">
	Adds two families with the names 'my_awesome_family' and 'my_less_awesome_inlaws' to the set of available firmware families.
	</example>
	"""

	def run(self, params, args):
		# Require at least one family name
		if not args:
			raise ArgRequired(self, 'family')

		# get rid of any duplicate names
		families = set(args)
		# ensure the family name doesn't already exist
		for family in families:
			if self.db.count('(id) FROM firmware_family WHERE name=%s', family) > 0:
				raise CommandError(cmd = self, msg = f'Firmware family with name {family} already exists.')

		self.runPlugins(args = families)

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

class Plugin(stack.commands.Plugin):
	"""Attempts to add all provided make names to the database."""

	def provides(self):
		return 'basic'

	def run(self, args):
		# Require at least one make name
		if not args:
			raise ArgRequired(self.owner, 'make')

		# get rid of any duplicate names
		makes = set(args)
		# ensure the make name doesn't already exist
		existing_makes = [
			make
			for make, count in (
				(make, self.owner.db.count('(id) FROM firmware_make WHERE name=%s', make)) for make in makes
			)
			if count > 0
		]
		if existing_makes:
			raise CommandError(cmd = self.owner, msg = f'The following firmware makes already exist: {existing_makes}.')

		for make in args:
			self.owner.db.execute(
				'''
				INSERT INTO firmware_make (
					name
				)
				VALUES (%s)
				''',
				make
			)

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
from stack.exception import ArgRequired, ArgError, CommandError

class Plugin(stack.commands.Plugin):
	"""Attempts to add all provided make names to the database."""

	def provides(self):
		return 'basic'

	def run(self, args):
		# Require at least one make name
		if not args:
			raise ArgRequired(cmd = self.owner, arg = 'make')

		# get rid of any duplicate names
		makes = self.owner.remove_duplicates(args = args)
		# ensure the make names don't already exist
		try:
			self.owner.validate_unique_makes(makes = makes)
		except CommandError as exception:
			raise ArgError(cmd = self.owner, arg = 'make', msg = exception.message())

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

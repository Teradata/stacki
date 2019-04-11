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
from stack.util import unique_everseen, lowered
from stack.exception import ArgRequired, ArgError, CommandError

class Plugin(stack.commands.Plugin):
	"""Attempts to add all provided make names to the database."""

	def provides(self):
		return "basic"

	def run(self, args):
		# get rid of any duplicate names
		makes = tuple(unique_everseen(lowered(args)))
		# ensure the make names don't already exist
		self.owner.ensure_unique_makes(makes = makes)

		self.owner.db.execute(
			"""
			INSERT INTO firmware_make (
				name
			)
			VALUES (%s)
			""",
			[(make,) for make in makes],
			many = True,
		)

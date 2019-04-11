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
from stack.util import lowered, unique_everseen
from stack.exception import ArgRequired

class Plugin(stack.commands.Plugin):
	"""Attempts to disassociate version_regexes from makes."""

	def provides(self):
		return "basic"

	def run(self, args):
		# Require make names
		if not args:
			raise ArgRequired(cmd = self.owner, arg = "makes")
		# lowercase all args and remove any duplicates
		args = tuple(unique_everseen(lowered(args)))
		# The makes must exist
		self.owner.ensure_makes_exist(makes = args)

		# disassociate the makes from version_regexes
		self.owner.db.execute("UPDATE firmware_make SET version_regex_id=NULL WHERE name IN %s", (args,))

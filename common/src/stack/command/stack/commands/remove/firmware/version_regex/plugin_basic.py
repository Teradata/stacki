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
	"""Attempts to remove version_regexes."""

	def provides(self):
		return "basic"

	def run(self, args):
		# lowercase all args and remove any duplicates
		names = tuple(unique_everseen(lowered(args)))
		# The version_regexes must exist
		self.owner.ensure_version_regexes_exist(names = names)

		# remove the version_regexes
		self.owner.db.execute("DELETE FROM firmware_version_regex WHERE name IN %s", (names,))

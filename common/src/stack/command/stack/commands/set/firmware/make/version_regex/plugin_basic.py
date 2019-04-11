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
from stack.exception import ArgRequired, ParamRequired, ParamError

class Plugin(stack.commands.Plugin):
	"""Attempts to associate a version_regex with makes."""

	def provides(self):
		return "basic"

	def run(self, args):
		params, args = args
		makes = tuple(unique_everseen(lowered(args)))

		version_regex, = lowered(
			self.owner.fillParams(names = [("version_regex", "")], params = params),
		)

		# The makes must exist
		self.owner.ensure_makes_exist(makes = makes)
		# The version_regex must exist
		self.owner.ensure_version_regex_exists(name = version_regex)

		# get the version_regex ID
		version_regex_id = self.owner.get_version_regex_id(name = version_regex)
		# associate the makes with the version_regex
		self.owner.db.execute(
			"UPDATE firmware_make SET version_regex_id=%s WHERE name in %s",
			(version_regex_id, makes),
		)

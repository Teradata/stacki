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

class Plugin(stack.commands.Plugin):
	"""Returns the names of all version regexes in the database."""

	def provides(self):
		return 'basic'

	def run(self, args):
		return {
			'keys': ['name', 'regex', 'description'],
			'values': [(row[0], row[1:]) for row in self.owner.db.select('name, regex, description FROM firmware_version_regex')]
		}

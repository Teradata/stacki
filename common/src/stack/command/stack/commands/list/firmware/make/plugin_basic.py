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
	"""Returns the names of all makes in the database."""

	def provides(self):
		return "basic"

	def run(self, args):
		# If expanded is true, also list any user defined implementations and version regexes
		if args:
			return {
				"keys": ["make", "version_regex_name"],
				"values": [
					(row[0], row[1:]) for row in self.owner.db.select(
						"""
						firmware_make.name, firmware_version_regex.name
						FROM firmware_make
							LEFT JOIN firmware_version_regex
								ON firmware_make.version_regex_id = firmware_version_regex.id
						"""
					)
				]
			}

		# Otherwise just return the names of the makes.
		return {
			"keys": ["make"],
			"values": [(row[0], []) for row in self.owner.db.select("name FROM firmware_make")]
		}

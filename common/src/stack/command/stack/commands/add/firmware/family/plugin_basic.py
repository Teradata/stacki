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
	"""Attempts to add all provided family names to the database."""

	def provides(self):
		return 'basic'

	def run(self, args):
		for family in args:
			self.owner.db.execute(
				'''
				INSERT INTO firmware_family (
					name
				)
				VALUES (%s)
				''',
				family
			)

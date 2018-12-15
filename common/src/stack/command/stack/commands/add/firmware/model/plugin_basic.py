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
	"""Attempts to add all provided model names to the database associated with the given make."""

	def provides(self):
		return 'basic'

	def run(self, args):
		models, make = args
		for model in models:
			self.owner.db.execute(
				'''
				INSERT INTO firmware_model (
					name,
					make_id
				)
				VALUES (%s, %s)
				''',
				(model, make)
			)

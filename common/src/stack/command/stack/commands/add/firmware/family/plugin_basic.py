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
from stack.exception import ArgRequired, ArgError

class Plugin(stack.commands.Plugin):
	"""Attempts to add all provided family names to the database."""

	def provides(self):
		return 'basic'

	def run(self, args):
		# Require at least one family name
		if not args:
			raise ArgRequired(cmd = self.owner, arg = 'family')

		# get rid of any duplicate names
		families = tuple(set(args))
		# ensure the family name doesn't already exist
		existing_families = [
			family
			for family, count in (
				(family, self.owner.db.count('(id) FROM firmware_family WHERE name=%s', family)) for family in families
			)
			if count > 0
		]
		if existing_families:
			raise ArgError(cmd = self.owner, arg = 'family', msg = f'The following firmware families already exist: {existing_families}.')

		for family in families:
			self.owner.db.execute(
				'''
				INSERT INTO firmware_family (
					name
				)
				VALUES (%s)
				''',
				family
			)

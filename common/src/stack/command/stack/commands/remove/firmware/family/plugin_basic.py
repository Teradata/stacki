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
	"""Attempts to remove all provided family names from the database."""

	def provides(self):
		return 'basic'

	def run(self, args):
		# Require at least one family name
		if not args:
			raise ArgRequired(self.owner, 'family')

		# get rid of any duplicate names
		families = set(args)
		# ensure the family names already exist
		missing_families = [
			family
			for family, count in (
				(family, self.owner.db.count('(id) FROM firmware_family WHERE name=%s', family)) for family in families
			)
			if count == 0
		]
		if missing_families:
			raise ArgError(cmd = self.owner, arg = 'family', msg = f"The following firmware families don't exist: {missing_families}.")

		# remove associated firmware
		for family in families:
			# get all the firmware associated with this family
			firmware_to_remove = [
				row[0] for row in
				self.owner.db.select(
					'''
					firmware.version
					FROM firmware
						INNER JOIN firmware_family
							ON firmware.family_id=firmware_family.id
					WHERE firmware_family.name=%s
					''',
					family
				)
			]
			# and remove it
			self.owner.call('remove.firmware', args = [" ".join(firmware_to_remove), f'family={family}'])

		# now delete the families
		self.owner.db.execute(
			'''
			DELETE FROM firmware_family WHERE name in (%s)
			''',
			", ".join(families)
		)

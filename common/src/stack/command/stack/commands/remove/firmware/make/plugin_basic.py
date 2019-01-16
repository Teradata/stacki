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
from stack.exception import ArgRequired, ArgError, CommandError

class Plugin(stack.commands.Plugin):
	"""Attempts to remove all provided makes and any associated models from the database."""

	def provides(self):
		return 'basic'

	def run(self, args):
		# Require at least one family name
		if not args:
			raise ArgRequired(self.owner, 'make')

		# get rid of any duplicate names
		makes = self.owner.remove_duplicates(args)
		# ensure the family names already exist
		try:
			self.owner.validate_makes_exist(makes = makes)
		except CommandError as exception:
			raise ArgError(cmd = self.owner, arg = 'make', msg = exception.message())

		# remove associated models
		for make in makes:
			# get all the models associated with this make
			models_to_remove = [
				row[0] for row in
				self.owner.db.select(
					'''
					firmware_model.name
					FROM firmware_model
						INNER JOIN firmware_make
							ON firmware_model.make_id=firmware_make.id
					WHERE firmware_make.name=%s
					''',
					make
				)
				if row
			]
			# and remove them if we found any
			if models_to_remove:
				self.owner.call('remove.firmware.model', args = [*models_to_remove, f'make={make}'])

		# now delete the makes
		self.owner.db.execute(
			'DELETE FROM firmware_make WHERE name IN %s',
			(makes, )
		)

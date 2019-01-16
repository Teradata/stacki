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
from stack.exception import ArgRequired, ArgError, ParamError, ParamRequired, CommandError
from pathlib import Path

class Plugin(stack.commands.Plugin):
	"""Attempts to remove all provided models from the system."""

	def provides(self):
		return 'basic'

	def run(self, args):
		# Require at least one model name
		params, args = args
		make, = self.owner.fillParams(
			names = [('make', None),],
			params = params
		)
		if not args:
			raise ArgRequired(cmd = self.owner, arg = 'model')

		if make is None:
			raise ParamRequired(cmd = self.owner, param = 'make')

		# get rid of any duplicate names
		models = self.owner.remove_duplicates(args)
		# ensure the make name already exists
		if not self.owner.make_exists(make = make):
			raise ParamError(cmd = self.owner, param = 'make', msg = f"The firmware make {make} doesn't exist.")
		# ensure the models exist
		try:
			self.owner.validate_models_exist(make, models)
		except CommandError as exception:
			raise ArgError(
				cmd = self.owner,
				arg = 'model',
				msg = exception.message()
			)

		# remove associated firmware
		for model in models:
			# get all the firmware associated with this make and model
			firmware_to_remove = [
				row[0] for row in
				self.owner.db.select(
					'''
					firmware.version
					FROM firmware
						INNER JOIN firmware_model
							ON firmware.model_id=firmware_model.id
						INNER JOIN firmware_make
							ON firmware_model.make_id=firmware_make.id
					WHERE firmware_make.name=%s AND firmware_model.name=%s
					''',
					(make, model)
				)
				if row
			]
			# and remove them if we found any
			if firmware_to_remove:
				self.owner.call('remove.firmware', args = [*firmware_to_remove, f'make={make}', f'model={model}'])

		# now delete the models
		self.owner.db.execute(
			'''
			DELETE firmware_model FROM firmware_model
				INNER JOIN firmware_make
					ON firmware_model.make_id=firmware_make.id
			WHERE firmware_model.name IN %s AND firmware_make.name=%s
			''',
			(models, make)
		)
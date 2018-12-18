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
from stack.exception import ArgRequired, ArgError, ParamError, ParamRequired
from pathlib import Path

class Plugin(stack.commands.Plugin):
	"""Attempts to remove all provided models from the system."""

	def provides(self):
		return 'basic'

	def run(self, args):
		# Require at least one family name
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
		models = tuple(set(args))
		# ensure the make name already exists
		if not self.owner.db.count('(id) FROM firmware_make WHERE name=%s', make):
			raise ParamError(cmd = self.owner, param = 'make', msg = f"The firmware make {make} doesn't exist.")
		# ensure the models exist
		missing_models = [
			model
			for model, count in (
				(
					model,
					self.owner.db.count(
						'''
						(firmware_model.id)
						FROM firmware_model
							INNER JOIN firmware_make
								ON firmware_model.make_id=firmware_make.id
						WHERE firmware_make.name=%s AND firmware_model.name=%s
						''',
						(make, model)
					)
				)
				for model in models
			)
			if count == 0
		]
		if missing_models:
			raise ArgError(
				cmd = self.owner,
				arg = 'model',
				msg = f"The following firmware models don't exist for make {make}: {missing_models}."
			)

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
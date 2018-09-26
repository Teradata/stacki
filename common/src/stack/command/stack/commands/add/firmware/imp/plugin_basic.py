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

from contextlib import ExitStack
from functools import partial
import stack.commands
from stack.exception import ArgRequired, ArgUnique, ArgError, ParamRequired, ParamError

class Plugin(stack.commands.Plugin):
	"""Attempts to add an implementation to the database and associate it appropriately."""

	def provides(self):
		return 'basic'

	def run(self, args):
		params, args = args
		make, models, = self.owner.fillParams(
			names = [('make', ''), ('models', ''),],
			params = params
		)
		# Require a implementation name
		if not args:
			raise ArgRequired(cmd = self.owner, arg = 'name')
		# Should only be one
		if len(args) != 1:
			raise ArgUnique(cmd = self.owner, arg = 'name')

		imp = args[0]
		# Should not already exist
		if self.owner.imp_exists(imp = imp):
			raise ArgError(
				cmd = self.owner,
				arg = 'name',
				msg = f'An implementation named {imp} already exists in the database.',
			)
		# Process the make if present.
		if make:
			# The make must exist
			if not self.owner.make_exists(make = make):
				raise ParamError(
					cmd = self.owner,
					param = 'make',
					msg = f'The make {make} does not exist.'
				)
		# Process models if specified
		if models:
			# A make is now required
			if not make:
				raise ParamRequired(cmd = self.owner, param = 'make')

			models = self.owner.remove_duplicates(
				args = (model.strip() for model in models.split(',') if model.strip())
			)
			# The models must exist
			self.owner.validate_models_exist(make = make, models = models)

		with ExitStack() as cleanup:
			# add the imp
			self.owner.db.execute(
				'''
				INSERT INTO firmware_imp (
					name
				)
				VALUES (%s)
				''',
				args
			)
			cleanup.callback(partial(self.owner.call, command = 'remove.firmware.imp', args = [imp]))

			# If models are specified, associate it with the relevant models for the given make
			if models:
				self.owner.call(command = 'set.firmware.model.imp', args = [*models, f'make={make}', f'imp={imp}'])
			# else if the make is specified, associate it with just the make
			elif make:
				self.owner.call(command = 'set.firmware.make.imp', args = [make, f'imp={imp}'])
			# else no association, just put it in the database.

			# everything worked, dismiss cleanup
			cleanup.pop_all()

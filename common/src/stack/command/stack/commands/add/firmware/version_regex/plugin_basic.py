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

import re
from contextlib import ExitStack
from functools import partial
import stack.commands
from stack.exception import ArgError, ArgRequired, ArgUnique, ParamRequired, ParamError

class Plugin(stack.commands.Plugin):
	"""Attempts to add all provided make names to the database."""

	def provides(self):
		return 'basic'

	def run(self, args):
		params, args = args
		name, description, make, models = self.owner.fillParams(
			names = [
				('name', ''),
				('description', ''),
				('make', ''),
				('models', ''),
			],
			params = params
		)
		# Require a version regex
		if not args:
			raise ArgRequired(cmd = self.owner, arg = 'regex')
		# Should only be one
		if len(args) != 1:
			raise ArgUnique(cmd = self.owner, arg = 'regex')
		# A name is required
		if not name:
			raise ParamRequired(cmd = self.owner, param = 'name')
		# The name must not already exist
		if self.owner.version_regex_exists(name = name):
			raise ParamError(
				cmd = self.owner,
				param = 'name',
				msg = f'A version_regex with the name {name} already exists in the database.'
			)
		# Require the version_regex to be a valid regex
		version_regex = args[0]
		try:
			re.compile(version_regex)
		except re.error as exception:
			raise ArgError(
				cmd = self.owner,
				arg = 'regex',
				msg = f'Invalid regex supplied: {exception}.'
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
			# add the regex
			self.owner.db.execute(
				'''
				INSERT INTO firmware_version_regex (
					regex,
					name,
					description
				)
				VALUES (%s, %s, %s)
				''',
				(version_regex, name, description)
			)
			cleanup.callback(partial(self.owner.call, command = 'remove.firmware.version_regex', args = [name]))

			# If models are specified, associate it with the relevant models for the given make
			if models:
				self.owner.call(command = 'set.firmware.model.version_regex', args = [*models, f'make={make}', f'version_regex={name}'])
			# else if the make is specified, associate it with just the make
			elif make:
				self.owner.call(command = 'set.firmware.make.version_regex', args = [make, f'version_regex={name}'])
			# else no association, just put it in the database.

			# everything worked, dismiss cleanup
			cleanup.pop_all()

# @copyright@
# Copyright (c) 2006 - 2019 Teradata
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
from stack.exception import ArgRequired, ParamRequired, ParamError

class Plugin(stack.commands.Plugin):
	"""Attempts to associate an implementation with models."""

	def provides(self):
		return 'basic'

	def run(self, args):
		params, args = args
		make, version_regex, = self.owner.fillParams(
			names = [
				('make', ''),
				('version_regex', ''),
			],
			params = params
		)
		# Require model names
		if not args:
			raise ArgRequired(cmd = self.owner, arg = 'models')

		args = self.owner.remove_duplicates(args = args)
		# The models must exist
		self.owner.validate_models_exist(models = args)
		# A make is required
		if not make:
			raise ParamRequired(cmd = self.owner, param = 'make')
		# The make must exist
		if not self.owner.make_exists(make = make):
			raise ParamError(
				cmd = self.owner,
				param = 'make',
				msg = f'The make {make} does not exist.'
			)
		# A version_regex is required
		if not version_regex:
			raise ParamRequired(cmd = self.owner, param = 'version_regex')
		# The version_regex must exist
		if not self.owner.version_regex_exists(name = version_regex):
			raise ParamError(
				cmd = self.owner,
				param = 'version_regex',
				msg = f'The version_regex {version_regex} does not exist in the database.'
			)

		# get the version_regex ID
		version_regex_id = self.owner.get_version_regex_id(name = version_regex)
		# associate the models with the version_regex
		self.owner.db.execute(
			"""
			UPDATE firmware_model
				INNER JOIN firmware_make ON firmware_make.id = firmware_model.make_id
			SET firmware_model.version_regex_id=%s WHERE firmware_model.name IN %s AND firmware_make.name=%s
			""",
			(version_regex_id, args, make)
		)

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
	"""Attempts to disassociate implementations from models."""

	def provides(self):
		return 'basic'

	def run(self, args):
		params, args = args
		make, = self.owner.fillParams(
			names = [('make', ''),],
			params = params
		)
		# Require model names
		if not args:
			raise ArgRequired(cmd = self.owner, arg = 'models')
		# The make must be provided
		if not make:
			raise ParamRequired(cmd = self.owner, param = 'make')
		# The make must exist
		if not self.owner.make_exists(make = make):
			raise ParamError(
				cmd = self.owner,
				param = 'make',
				msg = f'The make {make} does not exist.'
			)
		# remove any duplicates
		args = self.owner.remove_duplicates(args = args)
		# The models must exist
		self.owner.validate_models_exist(models = args, make = make)

		# disassociate the models from implementations
		self.owner.db.execute(
			"""
			UPDATE firmware_model
				INNER JOIN firmware_make ON firmware_make.id = firmware_model.make_id
			SET firmware_model.imp_id=NULL WHERE firmware_model.name IN %s AND firmware_make.name=%s
			""",
			(args, make)
		)

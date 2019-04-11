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
from stack.util import lowered, unique_everseen
from stack.exception import ArgRequired, ParamRequired, ParamError

class Plugin(stack.commands.Plugin):
	"""Attempts to disassociate version_regexes from models."""

	def provides(self):
		return "basic"

	def validate_args(self, args):
		"""We require the model names to be passed as arguments."""
		# Require model names
		if not args:
			raise ArgRequired(cmd = self.owner, arg = "models")

	def validate_make(self, make):
		"""Require a make and make sure it exists."""
		# The make must be provided
		if not make:
			raise ParamRequired(cmd = self.owner, param = "make")
		# The make must exist
		if not self.owner.make_exists(make = make):
			raise ParamError(
				cmd = self.owner,
				param = "make",
				msg = f"The make {make} does not exist.",
			)

	def run(self, args):
		params, args = args
		self.validate_args(args = args)
		# Lowercase all args and remove any duplicates.
		args = tuple(unique_everseen(lowered(args)))

		make, = lowered(
			self.owner.fillParams(names = [("make", "")], params = params)
		)
		self.validate_make(make = make)

		# The models must exist for the given make.
		self.owner.ensure_models_exist(models = args, make = make)

		# disassociate the models from version_regexes
		self.owner.db.execute(
			"""
			UPDATE firmware_model
				INNER JOIN firmware_make ON firmware_make.id = firmware_model.make_id
			SET firmware_model.version_regex_id=NULL WHERE firmware_model.name IN %s AND firmware_make.name=%s
			""",
			(args, make),
		)

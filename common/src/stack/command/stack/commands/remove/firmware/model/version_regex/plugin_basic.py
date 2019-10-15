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

	def run(self, args):
		params, args = args
		# Lowercase all args and remove any duplicates.
		models = tuple(unique_everseen(lowered(args)))

		make, = lowered(
			self.owner.fillParams(names = [("make", "")], params = params)
		)
		# The make and models must exist.
		self.owner.ensure_models_exist(models = models, make = make)

		# disassociate the models from version_regexes
		self.owner.db.execute(
			"""
			UPDATE firmware_model
				INNER JOIN firmware_make ON firmware_make.id = firmware_model.make_id
			SET firmware_model.version_regex_id=NULL WHERE firmware_model.name IN %s AND firmware_make.name=%s
			""",
			(models, make),
		)

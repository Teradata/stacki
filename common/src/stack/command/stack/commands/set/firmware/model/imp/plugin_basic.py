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
from stack.util import unique_everseen, lowered
from stack.exception import ArgRequired, ParamRequired, ParamError

class Plugin(stack.commands.Plugin):
	"""Attempts to associate an implementation with models."""

	def provides(self):
		return "basic"

	def run(self, args):
		params, args = args
		models = tuple(unique_everseen(lowered(args)))

		imp, make, = lowered(
			self.owner.fillParams(
				names = [
					("imp", ""),
					("make", ""),
				],
				params = params,
			),
		)
		self.owner.ensure_models_exist(make = make, models = models)
		self.owner.ensure_imp_exists(imp = imp)

		# get the implementation ID
		imp_id = self.owner.get_imp_id(imp = imp)
		# associate the models with the imp
		self.owner.db.execute(
			"""
			UPDATE firmware_model
				INNER JOIN firmware_make
					ON firmware_model.make_id = firmware_make.id
			SET firmware_model.imp_id=%s
			WHERE firmware_make.name = %s AND firmware_model.name IN %s
			""",
			(imp_id, make, models),
		)

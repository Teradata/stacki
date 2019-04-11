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
	"""Attempts to associate a version_regex with models."""

	def provides(self):
		return "basic"

	def run(self, args):
		params, args = args
		# Lowercase and make all args unique.
		models = tuple(unique_everseen(lowered(args)))

		make, version_regex, = lowered(
			self.owner.fillParams(
				names = [
					("make", ""),
					("version_regex", ""),
				],
				params = params,
			),
		)
		self.owner.ensure_models_exist(make = make, models = models)
		self.owner.ensure_version_regex_exists(name = version_regex)

		# get the version_regex ID
		version_regex_id = self.owner.get_version_regex_id(name = version_regex)
		# associate the models with the version_regex
		self.owner.db.execute(
			"""
			UPDATE firmware_model
				INNER JOIN firmware_make ON firmware_make.id = firmware_model.make_id
			SET firmware_model.version_regex_id=%s WHERE firmware_model.name IN %s AND firmware_make.name=%s
			""",
			(version_regex_id, models, make),
		)

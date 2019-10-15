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
from stack.util import unique_everseen, lowered
from stack.exception import ArgRequired, ArgError, ParamError, ParamRequired, CommandError
from pathlib import Path

class Plugin(stack.commands.Plugin):
	"""Attempts to remove all provided models from the system."""

	def provides(self):
		return "basic"

	def remove_related_firmware(self, make, models):
		"""Remove any firmware related to the provided make + model combinations."""
		for model in models:
			# get all the firmware associated with this make and model
			firmware_to_remove = [
				row[0] for row in
				self.owner.db.select(
					"""
					firmware.version
					FROM firmware
						INNER JOIN firmware_model
							ON firmware.model_id=firmware_model.id
						INNER JOIN firmware_make
							ON firmware_model.make_id=firmware_make.id
					WHERE firmware_make.name=%s AND firmware_model.name=%s
					""",
					(make, model),
				)
			]
			# and remove them if we found any
			if firmware_to_remove:
				self.owner.call(
					command = "remove.firmware",
					args = [*firmware_to_remove, f"make={make}", f"model={model}"],
				)

	def run(self, args):
		params, args = args
		make, = lowered(
			self.owner.fillParams(
				names = [("make", "")],
				params = params,
			)
		)

		# get rid of any duplicate names
		models = tuple(unique_everseen(lowered(args)))
		# ensure the make and models exist
		self.owner.ensure_models_exist(make = make, models = models)

		# remove associated firmware
		self.remove_related_firmware(make = make, models = models)

		# now delete the models
		self.owner.db.execute(
			"""
			DELETE firmware_model FROM firmware_model
				INNER JOIN firmware_make
					ON firmware_model.make_id=firmware_make.id
			WHERE firmware_model.name IN %s AND firmware_make.name=%s
			""",
			(models, make),
		)

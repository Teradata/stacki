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
from pathlib import Path
import inspect
from stack.util import lowered
import stack.commands
import stack.commands.list.host.firmware
import stack.commands.sync.host.firmware
from stack.exception import CommandError, ArgRequired, ArgUnique, ArgError, ParamRequired, ParamError

class Plugin(stack.commands.Plugin):
	"""Attempts to add an implementation to the database and optionally associate it with models."""

	def provides(self):
		return "basic"

	def validate_args(self, args):
		"""Validate that there is only one implementation name passed."""
		# Require a implementation name
		if not args:
			raise ArgRequired(cmd = self.owner, arg = "name")
		# Should only be one
		if len(args) != 1:
			raise ArgUnique(cmd = self.owner, arg = "name")

	def validate_imp(self, imp):
		"""Validate that the implementation doesn't already exist in the database, and that the implementation files are on disk."""
		# Should not already exist
		if self.owner.imp_exists(imp = imp):
			raise ArgError(
				cmd = self.owner,
				arg = "name",
				msg = f"An implementation named {imp} already exists in the database.",
			)

		# Should exist on disk
		list_firmware_imp = Path(
			inspect.getsourcefile(stack.commands.list.host.firmware),
		).parent.resolve() / f"imp_{imp}.py"
		sync_firmware_imp = Path(
			inspect.getsourcefile(stack.commands.sync.host.firmware),
		).parent.resolve() / f"imp_{imp}.py"
		if not list_firmware_imp.exists() or not sync_firmware_imp.exists():
			raise ArgError(
				cmd = self.owner,
				arg = "name",
				msg = (
					f"Could not find an implementation named imp_{imp}.py. Please ensure an"
					" implementation file is placed into each of the following locations:\n"
					f"{list_firmware_imp}\n{sync_firmware_imp}"
				),
			)

	def run(self, args):
		params, args = args
		self.validate_args(args = args)
		imp = args[0].lower()
		self.validate_imp(imp = imp)

		make, models, = lowered(
			self.owner.fillParams(
				names = [("make", ""), ("models", "")],
				params = params,
			)
		)
		# If either make or model are set, both arguments are required and must be valid.
		if make or models:
			# process a comma separated list of models
			models = [model.strip() for model in models.split(",") if model.strip()]
			self.owner.ensure_models_exist(make = make, models = models)

		with ExitStack() as cleanup:
			# Add the implementation
			self.owner.db.execute("INSERT INTO firmware_imp (name) VALUES (%s)", (imp,))
			cleanup.callback(self.owner.call, command = "remove.firmware.imp", args = [imp])

			# If the make and model are specified associate the imp with the make + model
			if make and models:
				self.owner.call(
					command = "set.firmware.model.imp",
					args = [*models, f"make={make}", f"imp={imp}"],
				)
			# else no association, just put it in the database.

			# everything worked, dismiss cleanup
			cleanup.pop_all()

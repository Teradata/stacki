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
import stack.commands
from stack.util import unique_everseen, lowered
from stack.exception import ArgRequired, CommandError, ParamRequired

class Plugin(stack.commands.Plugin):
	"""Attempts to add all provided model names to the database associated with the given make and implementation."""

	def provides(self):
		return "basic"

	def create_missing_make(self, make, cleanup):
		"""Create the make if it does not already exist."""
		if not self.owner.make_exists(make = make):
			self.owner.call(command = "add.firmware.make", args = [make])
			cleanup.callback(self.owner.call, command = "remove.firmware.make", args = [make])

	def create_missing_imp(self, imp, cleanup):
		"""Create the implementation if it does not already exist."""
		if not self.owner.imp_exists(imp = imp):
			self.owner.call(command = "add.firmware.imp", args = [imp])
			cleanup.callback(self.owner.call, command = "remove.firmware.imp", args = [imp])

	def run(self, args):
		params, args = args
		make, imp, = lowered(
			self.owner.fillParams(
				names = [
					("make", ""),
					("imp", ""),
				],
				params = params,
			),
		)

		# require a make
		if not make:
			raise ParamRequired(cmd = self.owner, param = "make")
		# require an implementation
		if not imp:
			raise ParamRequired(cmd = self.owner, param = "imp")

		# get rid of any duplicate names
		models = tuple(unique_everseen(lowered(args)))
		# ensure the model name doesn't already exist for the given make
		self.owner.ensure_unique_models(make = make, models = models)

		with ExitStack() as cleanup:
			# create the make if it doesn't already exist
			self.create_missing_make(make = make, cleanup = cleanup)
			# create the implementation if it doesn't already exist
			self.create_missing_imp(imp = imp, cleanup = cleanup)

			# get the ID of the make to associate with
			make_id = self.owner.get_make_id(make = make)
			# get the ID of the imp to associate with
			imp_id = self.owner.get_imp_id(imp = imp)

			self.owner.db.execute(
				"""
				INSERT INTO firmware_model (
					name,
					make_id,
					imp_id
				)
				VALUES (%s, %s, %s)
				""",
				[(model, make_id, imp_id) for model in models],
				many = True,
			)

			# everything was successful, dismiss cleanup.
			cleanup.pop_all()

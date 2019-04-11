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
from pathlib import Path
from contextlib import suppress

class Plugin(stack.commands.Plugin):
	"""Attempts to remove all provided firmware versions for the given make and model from the database and the file system."""

	def provides(self):
		return "basic"

	def validate_inputs(self, make, model, versions):
		"""Validate that the provided inputs are valid."""
		# process make if present
		if make:
			self.owner.ensure_make_exists(make = make)
		# process model if present
		if model:
			self.owner.ensure_model_exists(make = make, model = model)
		# Process versions if present
		if versions:
			self.owner.ensure_firmwares_exist(make = make, model = model, versions = versions)

	def build_query(self, make, model, versions):
		"""Build the select query based on the arguments."""
		query = """
			firmware.id, firmware.file
			FROM firmware
				INNER JOIN firmware_model
					ON firmware.model_id=firmware_model.id
				INNER JOIN firmware_make
					ON firmware_model.make_id=firmware_make.id
			WHERE {}
		"""
		query_params = []
		# If versions are specified, get the specific versions to remove
		if versions:
			query = query.format("firmware.version IN %s AND firmware_make.name=%s AND firmware_model.name=%s")
			query_params.extend((versions, make, model))
		# Else if make and model are specified, remove all firmwares for that make and model
		elif make and model:
			query = query.format("firmware_make.name=%s AND firmware_model.name=%s")
			query_params.extend((make, model))
		# Else if make is specified, remove all firmwares for that make
		elif make:
			query = query.format("firmware_make.name=%s")
			query_params.extend((make,))
		# otherwise remove all firmware
		else:
			query = "firmware.id, firmware.file FROM firmware"

		return query, query_params

	def run(self, args):
		params, args = args
		versions = tuple(unique_everseen(lowered(args)))
		make, model = lowered(
			self.owner.fillParams(
				names = [("make", ""), ("model", "")],
				params = params,
			)
		)
		self.validate_inputs(make = make, model = model, versions = versions)

		# Get the query and query_params based on the arguments and parameters.
		query, query_params = self.build_query(make = make, model = model, versions = versions)
		# remove the file and then the db entry for each firmware to remove
		for firmware_id, file_path in ((row[0], row[1]) for row in self.owner.db.select(query, query_params)):
			# If the file doesn't exist, that's ok since we were trying to delete it anyways.
			with suppress(FileNotFoundError):
				Path(file_path).resolve(strict = True).unlink()

			self.owner.db.execute("DELETE FROM firmware WHERE id=%s", firmware_id)

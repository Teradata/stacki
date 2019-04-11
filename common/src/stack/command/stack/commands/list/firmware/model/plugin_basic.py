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

class Plugin(stack.commands.Plugin):
	"""Returns the make name and model name of all models in the database."""

	def provides(self):
		return "basic"

	def validate_make(self, make):
		"""If a make is provided, ensure it exists."""
		if make:
			self.owner.ensure_make_exists(make = make)

	def validate_models(self, make, models):
		"""If models are provided, ensure both the make and the models exist."""
		if models:
			# This will also fail if the make is not provided or doesn't exist.
			self.owner.ensure_models_exist(make = make, models = models)

	def get_expanded_results(self, make, models):
		"""Return the expanded results set from the database.

		If make is provided, this will filter results to the ones that match the make.

		If both make and models are provided, this will filter the results to the ones that match
		on make and in models.
		"""
		query = """
			firmware_make.name, firmware_model.name, firmware_imp.name, firmware_version_regex.name
			FROM firmware_make
				INNER JOIN firmware_model
					ON firmware_model.make_id=firmware_make.id
				INNER JOIN firmware_imp
					ON firmware_model.imp_id=firmware_imp.id
				LEFT JOIN firmware_version_regex
					ON firmware_model.version_regex_id=firmware_version_regex.id
		"""
		query_params = []
		# Filter on make and models if both are provided.
		if make and models:
			query += " WHERE firmware_model.name IN %s AND firmware_make.name=%s"
			query_params.extend((models, make))
		# Filter on only make if models aren't provided but a make is.
		elif make:
			query += " WHERE firmware_make.name=%s"
			query_params.append(make)
		# Otherwise return everything

		return {
			"keys": ["make", "model", "implementation", "version_regex_name"],
			"values": [
				(row[0], row[1:])
				for row in self.owner.db.select(query, query_params)
			]
		}

	def get_results(self, make, models):
		"""Return the simple results set from the database.

		If make is provided, this will filter results to the ones that match the make.

		If both make and models are provided, this will filter the results to the ones that match
		on make and in models.
		"""
		query = """
			firmware_make.name, firmware_model.name
			FROM firmware_make
				INNER JOIN firmware_model
					ON firmware_model.make_id=firmware_make.id
		"""
		query_params = []
		# Filter on make and models if both are provided.
		if make and models:
			query += " WHERE firmware_model.name IN %s AND firmware_make.name=%s"
			query_params.extend((models, make))
		# Filter on only make if models aren't provided but a make is.
		elif make:
			query += " WHERE firmware_make.name=%s"
			query_params.append(make)
		# Otherwise return everything

		return {
			"keys": ["make", "model"],
			"values": [
				(row[0], row[1:])
				for row in self.owner.db.select(query, query_params)
			]
		}

	def run(self, args):
		params, args = args
		models = tuple(unique_everseen(lowered(args)))

		expanded, make = lowered(
			self.owner.fillParams(
				names = [("expanded", "false"), ("make", "")],
				params = params,
			)
		)
		expanded = self.owner.str2bool(expanded)
		self.validate_make(make = make)
		self.validate_models(make = make, models = models)

		# If expanded is true, also list the implementation and any version regex associated with the model.
		if expanded:
			return self.get_expanded_results(make = make, models = models)

		# Otherwise just return the names of the makes and models.
		return self.get_results(make = make, models = models)

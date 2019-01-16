from stack.exception import CommandError

class FirmwareArgumentProcessor:
	"""A mixin to process firmware command arguments."""

	def remove_duplicates(self, args):
		"""Takes a list of arguments and removes any duplicates.

		This returns a tuple of the now unique arguments.
		"""
		return tuple(set(args))

	def get_make_id(self, make):
		"""Get the ID of the make with the provided name.

		This will raise a CommandError if the make with the provided name doesn't exist.
		"""
		row = self.db.select('id FROM firmware_make WHERE name=%s', make)
		if not row:
			raise CommandError(cmd = self, msg = f"Firmware make {make} doesn't exist.")

		return row[0][0]

	def make_exists(self, make):
		"""Returns whether the given make exists in the database."""
		return self.db.count('(id) FROM firmware_make WHERE name=%s', make)

	def validate_unique_makes(self, makes):
		"""Validates that none of the names in the list of makes provided already exist in the database."""
		# ensure the make names don't already exist
		existing_makes = [
			make
			for make, exists in (
				(make, self.make_exists(make)) for make in makes
			)
			if exists
		]
		if existing_makes:
			raise CommandError(cmd = self, msg = f'The following firmware makes already exist: {existing_makes}.')

	def validate_makes_exist(self, makes):
		"""Validates that all of the names in the list of makes provided already exist in the datbase."""
		# ensure the family names already exist
		missing_makes = [
			make
			for make, exists in (
				(make, self.make_exists(make)) for make in makes
			)
			if not exists
		]
		if missing_makes:
			raise CommandError(cmd = self, msg = f"The following firmware makes don't exist: {missing_makes}.")

	def get_model_id(self, make, model):
		"""Get the ID of the model with the provided name related to the provided make.

		This will raise a CommandError if the make + model combo doesn't exist.
		"""
		row = self.db.select(
			'''
			firmware_model.id
			FROM firmware_model
				INNER JOIN firmware_make
					ON firmware_model.make_id=firmware_make.id
			WHERE firmware_make.name=%s AND firmware_model.name=%s
			''',
			(make, model)
		)
		if not row:
			raise CommandError(cmd = self, msg = f"Firmware model {model} doesn't exist for make {make}.")

		return row[0][0]

	def model_exists(self, make, model):
		"""Returns whether the given model exists for the given make."""
		return self.db.count(
			'''
			(firmware_model.id)
			FROM firmware_model
				INNER JOIN firmware_make
					ON firmware_model.make_id=firmware_make.id
			WHERE firmware_make.name=%s AND firmware_model.name=%s
			''',
			(make, model)
		)

	def validate_unique_models(self, make, models):
		"""Validates that none of the given model names already exist in the database for the given make."""
		# ensure the model name doesn't already exist for the given make
		existing_makes_models = [
			(make, model)
			for make, model, exists in (
				(make, model, self.model_exists(make, model)) for model in models
			)
			if exists
		]
		if existing_makes_models:
			raise CommandError(cmd = self, msg = f'The following make and model combinations already exist {existing_makes_models}.')

	def validate_models_exist(self, make, models):
		"""Validates that all of the given model names already exist in the database for the given make."""
		# ensure the models exist
		missing_models = [
			model
			for model, exists in (
				(model, self.model_exists(make, model)) for model in models
			)
			if not exists
		]
		if missing_models:
			raise CommandError(
				cmd = self.owner,
				msg = f"The following firmware models don't exist for make {make}: {missing_models}."
			)

	def firmware_exists(self, make, model, version):
		"""Returns whether the given firmware version exists for the make + model combo."""
		return self.db.count(
			'''
			(firmware.id)
			FROM firmware
				INNER JOIN firmware_model
					ON firmware.model_id=firmware_model.id
				INNER JOIN firmware_make
					ON firmware_model.make_id=firmware_make.id
			WHERE firmware_make.name=%s AND firmware_model.name=%s AND firmware.version=%s
			''',
			(make, model, version)
		)

	def validate_firmwares_exist(self, make, model, versions):
		"""Validates that all the firmware versions provided exist for the given make and model."""
		# ensure the versions exist in the DB
		missing_versions = [
			version
			for version, exists in (
				(version, self.firmware_exists(make, model, version)) for version in versions
			)
			if not exists
		]
		if missing_versions:
			raise CommandError(
				cmd = self.owner,
				msg = f"The following firmware versions don't exist for make {make} and model {model}: {missing_versions}."
			)

from pathlib import Path
from collections import namedtuple, OrderedDict
from stack.exception import CommandError

class FirmwareArgumentProcessor:
	"""A mixin to process firmware command arguments."""

	def get_make_id(self, make):
		"""Get the ID of the make with the provided name.

		This will raise a CommandError if the make with the provided name doesn't exist.
		"""
		row = self.db.select("id FROM firmware_make WHERE name=%s", make)
		if not row:
			raise CommandError(cmd = self, msg = f"Firmware make {make} doesn't exist.")

		return row[0][0]

	def make_exists(self, make):
		"""Returns whether the given make exists in the database."""
		return self.db.count("(id) FROM firmware_make WHERE name=%s", make)

	def ensure_make_exists(self, make):
		"""Ensures that the provided make exists.

		If the make does not exist in the database, a CommandError is raised.

		If an empty string is provided, a CommandError is raised.
		"""
		if not make:
			raise CommandError(cmd = self, msg = "A make is required.")

		if not self.make_exists(make = make):
			raise CommandError(cmd = self, msg = f"The make {make} does not exist.")

	def ensure_unique_makes(self, makes):
		"""Ensures that none of the names in the list of makes provided already exist in the database.

		If an empty iterable is provided, a CommandError is raised.

		If any make name is blank, a CommandError is raised.
		"""
		makes = tuple(makes)
		if not makes:
			raise CommandError(cmd = self, msg = "Makes are required.")

		# No empty strings allowed.
		if not all(makes):
			raise CommandError(cmd = self, msg = "A make cannot be an empty string.")

		# ensure the make names don't already exist
		existing_makes = [
			make
			for make, exists in (
				(make, self.make_exists(make)) for make in makes
			)
			if exists
		]
		if existing_makes:
			raise CommandError(cmd = self, msg = f"The following firmware makes already exist: {existing_makes}.")

	def ensure_makes_exist(self, makes):
		"""Ensures that all of the names in the list of makes provided already exist in the datbase.

		If an empty iterable is provided, a CommandError is raised.

		If any make name is blank, a CommandError is raised.
		"""
		makes = tuple(makes)
		if not makes:
			raise CommandError(cmd = self, msg = "Makes are required.")

		# No empty strings allowed.
		if not all(makes):
			raise CommandError(cmd = self, msg = "A make cannot be an empty string.")

		# ensure the make names already exist
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
			"""
			firmware_model.id
			FROM firmware_model
				INNER JOIN firmware_make
					ON firmware_model.make_id=firmware_make.id
			WHERE firmware_make.name=%s AND firmware_model.name=%s
			""",
			(make, model),
		)
		if not row:
			raise CommandError(cmd = self, msg = f"Firmware model {model} doesn't exist for make {make}.")

		return row[0][0]

	def model_exists(self, make, model):
		"""Returns whether the given model exists for the given make."""
		return self.db.count(
			"""
			(firmware_model.id)
			FROM firmware_model
				INNER JOIN firmware_make
					ON firmware_model.make_id=firmware_make.id
			WHERE firmware_make.name=%s AND firmware_model.name=%s
			""",
			(make, model),
		)

	def ensure_model_exists(self, make, model):
		"""Ensures that a given model exists for a given make.

		If the make does not exist in the database, a CommandError is raised.

		If an empty string is provided for either make or model, a CommandError is raised.
		"""
		self.ensure_make_exists(make = make)

		if not model:
			raise CommandError(cmd = self, msg = "A model is required.")

		if not self.model_exists(make = make, model = model):
			raise CommandError(cmd = self, msg = f"Make {make} does not exist for model {model}.")

	def ensure_unique_models(self, make, models):
		"""Ensures that none of the given model names already exist in the database for the given make.

		If an empty iterable is provided, a CommandError is raised.

		If any model name is blank, a CommandError is raised.
		"""
		# We don't require that the make exists because a set of models for a non-existent make would be
		# entirely new in that they are going to be added under a make that doesn't already exist.
		models = tuple(models)
		if not models:
			raise CommandError(cmd = self, msg = "Models are required.")

		# No empty strings allowed.
		if not all(models):
			raise CommandError(cmd = self, msg = "A model cannot be an empty string.")

		# ensure the model name doesn't already exist for the given make
		existing_makes_models = [
			(make, model)
			for make, model, exists in (
				(make, model, self.model_exists(make, model)) for model in models
			)
			if exists
		]
		if existing_makes_models:
			raise CommandError(cmd = self, msg = f"The following make and model combinations already exist {existing_makes_models}.")

	def ensure_models_exist(self, make, models):
		"""Ensures that all of the given model names already exist in the database for the given make.

		If the make does not exist, a CommandError is raised.

		If an empty iterable is provided, a CommandError is raised.

		If an empty string is provided for either make or one of the models, a CommandError is raised.

		If any model name is blank, a CommandError is raised.
		"""
		self.ensure_make_exists(make = make)

		models = tuple(models)
		if not models:
			raise CommandError(cmd = self, msg = "Models are required.")

		# No empty strings allowed.
		if not all(models):
			raise CommandError(cmd = self, msg = "A model cannot be an empty string.")

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
				cmd = self,
				msg = f"The following firmware models don't exist for make {make}: {missing_models}."
			)

	def firmware_exists(self, make, model, version):
		"""Returns whether the given firmware version exists for the make + model combo."""
		return self.db.count(
			"""
			(firmware.id)
			FROM firmware
				INNER JOIN firmware_model
					ON firmware.model_id=firmware_model.id
				INNER JOIN firmware_make
					ON firmware_model.make_id=firmware_make.id
			WHERE firmware_make.name=%s AND firmware_model.name=%s AND firmware.version=%s
			""",
			(make, model, version)
		)

	def ensure_firmware_exists(self, make, model, version):
		"""Ensure that the provided firmware version for the make and model exists.

		If the make does not exist, a CommandError is raised.

		If the model does not exist, a CommandError is raised.

		If an empty string is provided for make, model, or version, a CommandError is raised.
		"""
		self.ensure_model_exists(make = make, model = model)

		if not version:
			raise CommandError(cmd = self, msg = "A version is required.")

		if not self.firmware_exists(make = make, model = model, version = version):
			raise CommandError(
				cmd = self,
				msg = f"The firmware version {version} does not exist for make {make} and model {model}.",
			)

	def ensure_firmwares_exist(self, make, model, versions):
		"""Ensures that all the firmware versions provided exist for the given make and model.

		If the make does not exist, a CommandError is raised.

		If the model does not exist, a CommandError is raised.

		If an empty iterable is provided, a CommandError is raised.

		If an empty string is provided for make, model, or version, a CommandError is raised.
		"""
		self.ensure_model_exists(make = make, model = model)

		versions = tuple(versions)
		if not versions:
			raise CommandError(cmd = self, msg = "Versions are required.")

		# No empty strings allowed.
		if not all(versions):
			raise CommandError(cmd = self, msg = "A version cannot be an empty string.")

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
				cmd = self,
				msg = f"The following firmware versions don't exist for make {make} and model {model}: {missing_versions}."
			)

	def get_firmware_id(self, make, model, version):
		"""Get the ID of the firmware version with the provided version for the provided make and model.

		This will raise a CommandError if the firmware version matching the provided information doesn't exist.
		"""
		row = self.db.select(
			"""
			firmware.id
			FROM firmware
				INNER JOIN firmware_model
					ON firmware.model_id=firmware_model.id
				INNER JOIN firmware_make
					ON firmware_model.make_id=firmware_make.id
			WHERE firmware_make.name=%s AND firmware_model.name=%s AND firmware.version=%s
			""",
			(make, model, version)
		)
		if not row:
			raise CommandError(cmd = self, msg = f"Firmware version {version} doesn't exist for make {make} and model {model}.")

		return row[0][0]

	def get_common_frontend_ip(self, hostname):
		"""Attempts to get an IP of one of the front end interfaces that shares a network with the provided host.

		If the frontend and the host have no common networks, a CommandError is raised.
		If none of the interfaces on the common network have IP addresses, a CommandError is raised.
		"""
		host_interface_frontend = self.call(command = "list.host.interface", args = ["a:frontend"])
		# try to get the set of all common networks between the front end and the target host
		host_networks = set(host["network"] for host in self.call(command = "list.host.interface", args = [hostname]))
		frontend_networks = set(frontend_interface["network"] for frontend_interface in host_interface_frontend)
		common_networks = list(host_networks & frontend_networks)

		if not common_networks:
			raise CommandError(
				cmd = self,
				msg = (
					f"{hostname} does not share a network with the frontend, and thus cannot fetch firmware"
					f" from it. Please configure {hostname} to share a common network with the frontend."
				)
			)

		# try to get the IP addresses of frontend interfaces on the common networks
		ip_addr = [
			frontend_interface["ip"] for frontend_interface in host_interface_frontend
			if frontend_interface["network"] in common_networks and frontend_interface["ip"]
		]

		if not ip_addr:
			raise CommandError(
				cmd = self,
				msg = (
					f"None of the network interfaces on the frontend attached to the following common networks"
					f"have an IP address. Please configure at least one interface to have an IP address on one"
					f"of the following networks: {common_networks}"
				)
			)
		# pick the first one and use it
		return ip_addr[0]

	def get_firmware_url(self, hostname, firmware_file):
		"""Attempts to get a url to allow a backend to download the provided firmware file from the front end.

		If the frontend and the backend have no common networks, a CommandError is raised.
		If none of the interfaces on the common network have IP addresses, a CommandError is raised.
		If the file doesn't exist on disk, a CommandError is raised.
		"""
		try:
			firmware_file = Path(firmware_file).resolve(strict = True)
		except FileNotFoundError as exception:
			raise CommandError(
				cmd = self,
				msg = f"Cannot resolve frontend URL for firmware file that does not exist: {exception}",
			)

		ip_addr = self.get_common_frontend_ip(hostname = hostname)
		# remove the /export/stack prefix from the file path, as /install points to /export/stack
		firmware_file = Path().joinpath(*(part for part in firmware_file.parts if part not in ("/", "export", "stack")))

		return f"http://{ip_addr}/install/{firmware_file}"

	def imp_exists(self, imp):
		"""Returns whether the given implementation name exists in the database."""
		return self.db.count("(id) FROM firmware_imp WHERE name=%s", imp)

	def ensure_imp_exists(self, imp):
		"""Ensures that the provided implementation exists in the database.

		If the provided name is an empty string, a CommandError is raised.

		If the imp name does not exist in the database, a CommandError is raised.
		"""
		if not imp:
			raise CommandError(cmd = self, msg = "Imp is required.")

		if not self.imp_exists(imp = imp):
			raise CommandError(cmd = self, msg = f"Imp {imp} does not exist in the database.")

	def ensure_imps_exist(self, imps):
		"""Ensures that all of the given imp names already exist in the database.

		If an empty iterable is provided, a CommandError is raised.

		If an empty string is provided for any imp name, a CommandError is raised.
		"""
		imps = tuple(imps)
		if not imps:
			raise CommandError(cmd = self, msg = "Imps are required.")

		# No empty strings allowed.
		if not all(imps):
			raise CommandError(cmd = self, msg = "A imp cannot be an empty string.")

		# ensure the imps exist
		missing_imps = [
			imp
			for imp, exists in (
				(imp, self.imp_exists(imp)) for imp in imps
			)
			if not exists
		]
		if missing_imps:
			raise CommandError(
				cmd = self,
				msg = f"The following firmware implementations don't exist in the database: {missing_imps}."
			)

	def get_imp_id(self, imp):
		"""Get the ID of the implementation with the provided name.

		This will raise a CommandError if the implementation with the provided name doesn't exist.
		"""
		row = self.db.select('id FROM firmware_imp WHERE name=%s', imp)
		if not row:
			raise CommandError(cmd = self, msg = f"Firmware implementation {imp} doesn't exist in the database.")

		return row[0][0]

	def version_regex_exists(self, name):
		"""Returns whether the given version_regex name exists in the database."""
		return self.db.count("(id) FROM firmware_version_regex WHERE name=%s", name)

	def ensure_version_regex_exists(self, name):
		"""Ensures that a version_regex with the provided name exists in the database.

		If the name is an empty string, a CommandError is raised.

		If the version_regex does not exist, a CommandError is raised.
		"""
		if not name:
			raise CommandError(cmd = self, msg = "A version regex name is required.")

		if not self.version_regex_exists(name = name):
			raise CommandError(cmd = self, msg = f"A version regex named {name} does not exist.")

	def ensure_version_regexes_exist(self, names):
		"""Ensures that all of the given version_regex names already exist in the database.

		If an empty iterable is provided, a CommandError is raised.

		If an empty string is provided for any version_regex name, a CommandError is raised.
		"""
		names = tuple(names)
		if not names:
			raise CommandError(cmd = self, msg = "Version regex names are required.")

		# No empty strings allowed.
		if not all(names):
			raise CommandError(cmd = self, msg = "A version regex name cannot be an empty string.")

		# ensure the version_regexes exist
		missing_version_regexes = [
			name
			for name, exists in (
				(name, self.version_regex_exists(name)) for name in names
			)
			if not exists
		]
		if missing_version_regexes:
			raise CommandError(
				cmd = self,
				msg = f"The following firmware version regexes don't exist in the database: {missing_version_regexes}."
			)

	def get_version_regex_id(self, name):
		"""Get the ID of the version_regex with the provided name.

		This will raise a CommandError if the version_regex with the provided name doesn't exist.
		"""
		row = self.db.select("id FROM firmware_version_regex WHERE name=%s", name)
		if not row:
			raise CommandError(cmd = self, msg = f"Firmware version_regex {name} doesn't exist in the database.")

		return row[0][0]

	def try_get_version_regex(self, make, model):
		"""Attempts to return the most relevant version regex for the make and model combination provided.

		If found, a namedtuple is returned with the members 'regex', 'name', and 'description'. The
		regex member is the actual regular expression to use for validation while name and description
		are the user friendly name and an optional description of the regex, respectively.

		A version regex set on the model will be preferred to one set on the make.

		If neither the make nor the model have a version regex set, None will be returned.
		"""
		regex = None
		row = self.db.select(
			"""
			make_regex.regex, make_regex.name, make_regex.description, model_regex.regex, model_regex.name, model_regex.description
			FROM firmware_make
				INNER JOIN firmware_model
					ON firmware_model.make_id = firmware_make.id
				LEFT JOIN firmware_version_regex as make_regex
					ON firmware_make.version_regex_id = make_regex.id
				LEFT JOIN firmware_version_regex as model_regex
					ON firmware_model.version_regex_id = model_regex.id
			WHERE firmware_make.name = %s AND firmware_model.name = %s
			""",
			(make, model)
		)
		if row:
			make_regex, make_regex_name, make_regex_description = row[0][0:3]
			model_regex, model_regex_name, model_regex_description = row[0][3:6]
			RegexInfo = namedtuple("RegexInfo", ("regex", "name", "description"))
			# prefer the model regex
			if model_regex:
				regex = RegexInfo(
					regex = model_regex,
					name = model_regex_name,
					description = model_regex_description
				)
			# else use the make regex
			elif make_regex:
				regex = RegexInfo(
					regex = make_regex,
					name = make_regex_name,
					description = make_regex_description
				)
			# Otherwise we return nothing.

		return regex

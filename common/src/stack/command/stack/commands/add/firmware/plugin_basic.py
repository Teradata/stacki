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
from stack.exception import ArgRequired, ArgUnique, ArgError, ParamRequired, ParamError
import stack.firmware
from stack.util import unique_everseen, lowered
from pathlib import Path
from contextlib import ExitStack
import re

class Plugin(stack.commands.Plugin):
	"""Attempts to add firmware to be tracked by stacki."""

	def provides(self):
		return "basic"

	def validate_args(self, args):
		"""Validate that a version number is provided and that there is only one."""
		# Require a version name
		if not args:
			raise ArgRequired(cmd = self.owner, arg = "version")
		# should only be one version name
		if len(args) != 1:
			raise ArgUnique(cmd = self.owner, arg = "version")

	def validate_required_params(self, source, make, model):
		"""Validate that the required parameters are provided."""
		# require a source
		if not source:
			raise ParamRequired(cmd = self.owner, param = "source")
		# require both make and model
		if not make:
			raise ParamRequired(cmd = self.owner, param = "make")
		if not model:
			raise ParamRequired(cmd = self.owner, param = "model")

	def validate_imp(self, make, model, imp):
		"""Validate whether an imp is required due to the model not already existing,
		and validate that if the model exists that any requested implementation matches.
		"""
		# require an implementation if the model does not exist.
		if not imp and not self.owner.model_exists(make = make, model = model):
			# Get the list of valid makes + models and add them to the error message in an attempt to be helpful
			makes_and_models = "\n".join(
				f"{make_model['make']} + {make_model['model']}" for make_model in
				self.owner.call(command = "list.firmware.model")
			)
			raise ParamError(
				cmd = self.owner,
				param = "imp",
				msg = (
					f"is required because make and model combination {make} + {model} doesn't exist."
					f" Did you mean to use one of the below makes and/or models?\n{makes_and_models}"
				),
			)
		# Raise an error if the implementation was provided for an already existing model, and it does not match.
		if imp and self.owner.model_exists(make = make, model = model):
			existing_imp = self.owner.call(
				command = "list.firmware.model",
				args = [model, f"make={make}"]
			)[0]["implementation"]

			if imp != existing_imp:
				raise ParamError(
					cmd = self.owner,
					param = "imp",
					msg = (
						f"The provided imp {imp} doesn't match the existing imp {existing_imp} for the already existing"
						f" make + model {make} + {model}. Did you not mean to specify an imp? The parameter is not required"
						" for existing models.\nIf you want to change what implementation is used, run"
						" 'stack set firmware model imp'."
					),
				)

	def validate_hash_alg_supported(self, hash_alg):
		"""Validates that the requested hash algorithm is supported."""
		try:
			stack.firmware.ensure_hash_alg_supported(hash_alg = hash_alg)
		except stack.firmware.FirmwareError as exception:
			raise ParamError(
				cmd = self.owner,
				param = "hash_alg",
				msg = f"{exception}",
			) from exception

	def validate_version(self, version, make, model):
		"""Attempts to validate the version number against a version_regex if one is set for the
		make or model provided as well as ensuring the firmware version doesn't already exist.
		"""
		# Attempt to get the version regex entry.
		regex = self.owner.try_get_version_regex(make = make, model = model)
		if regex and not re.search(pattern = regex.regex, string = version, flags = re.IGNORECASE):
			raise ArgError(
				cmd = self.owner,
				arg = "version",
				msg = (
					f"The format of the version number {version} does not validate based on the regex {regex.regex}"
					f" named {regex.name}{f' with description {regex.description}' if regex.description else ''}."
				),
			)

		if self.owner.firmware_exists(make = make, model = model, version = version):
			raise ArgError(
				cmd = self.owner,
				arg = "version",
				msg = f"The firmware version {version} for make {make} and model {model} already exists.",
			)

	def validate_inputs(self, source, make, model, version, imp, hash_alg):
		"""Validate the input params and version arg."""
		# Make sure all require parameters are present.
		self.validate_required_params(source = source, make = make, model = model)
		# Check if an implementation is required, and whether one was provided.
		self.validate_imp(make = make, model = model, imp = imp)
		# Validate that the hash algorithm is supported
		self.validate_hash_alg_supported(hash_alg = hash_alg)
		# validate the version matches the version_regex if one is set and that it doesn't already exist.
		self.validate_version(version = version, make = make, model = model)

	def create_missing_imp(self, imp, cleanup):
		"""Adds an implementation to the database if provided and it doesn't already exist."""
		# create the implementation if provided one and it doesn't already exist
		if imp and not self.owner.imp_exists(imp = imp):
			self.owner.call(command = "add.firmware.imp", args = [imp])
			cleanup.callback(self.owner.call, command = "remove.firmware.imp", args = [imp])

	def create_missing_make(self, make, cleanup):
		"""Adds a make to the database if it doesn't already exist."""
		# create the make if it doesn't already exist
		if not self.owner.make_exists(make = make):
			self.owner.call(command = "add.firmware.make", args = [make])
			cleanup.callback(self.owner.call, command = "remove.firmware.make", args = [make])

	def create_missing_model(self, make, model, imp, cleanup):
		"""Adds a model to the database if it doesn't already exist."""
		# create the model if it doesn't already exist
		if not self.owner.model_exists(make = make, model = model):
			self.owner.call(command = "add.firmware.model", args = [model, f"make={make}", f"imp={imp}"])
			cleanup.callback(self.owner.call, command = "remove.firmware.model", args = [model, f"make={make}"])

	def create_missing_related_entries(self, make, model, imp, cleanup):
		"""Create any missing related entries as necessary."""
		self.create_missing_imp(imp = imp, cleanup = cleanup)
		self.create_missing_make(make = make, cleanup = cleanup)
		self.create_missing_model(make = make, model = model, imp = imp, cleanup = cleanup)

	def file_cleanup(self, file_path):
		"""Remove the file if it exists.

		Needed because "stack remove firmware" also removes the file
		and that might have been run as part of the exit stack unwinding.
		"""
		if file_path.exists():
			file_path.unlink()

	def fetch_firmware(self, source, make, model, cleanup):
		"""Try to fetch the firmware from the source and return the path to the file."""
		try:
			file_path = stack.firmware.fetch_firmware(
				source = source,
				make = make,
				model = model,
			)

			cleanup.callback(self.file_cleanup, file_path = file_path)
			return file_path

		except stack.firmware.FirmwareError as exception:
			raise ParamError(
				cmd = self.owner,
				param = "source",
				msg = f"{exception}",
			) from exception

	def calculate_hash(self, file_path, hash_alg, hash_value):
		"""Calculate the file hash and verify it against the provided hash, if present."""
		try:
			return stack.firmware.calculate_hash(file_path = file_path, hash_alg = hash_alg, hash_value = hash_value)
		except stack.firmware.FirmwareError as exception:
			raise ParamError(
				cmd = self.owner,
				param = "hash",
				msg = f"{exception}",
			) from exception

	def add_firmware(self, source, make, model, version, imp, hash_value, hash_alg, cleanup):
		"""Adds a firmware file to be managed by stacki.

		This adds the file locally on disk as well as inserts metadata into the database.
		"""
		# fetch the firmware from the source and copy the firmware into a stacki managed file
		file_path = self.fetch_firmware(
			source = source,
			make = make,
			model = model,
			cleanup = cleanup,
		)
		# calculate the file hash and compare it with the user provided value if present.
		file_hash = self.calculate_hash(
			file_path = file_path,
			hash_alg = hash_alg,
			hash_value = hash_value,
		)
		# add imp, make, and model database entries if needed.
		self.create_missing_related_entries(make = make, model = model, imp = imp, cleanup = cleanup)

		# get the ID of the model to associate with
		model_id = self.owner.get_model_id(make, model)
		# insert into DB associated with make + model
		self.owner.db.execute(
			"""
			INSERT INTO firmware (
				model_id,
				source,
				version,
				hash_alg,
				hash,
				file
			)
			VALUES (%s, %s, %s, %s, %s, %s)
			""",
			(model_id, source, version, hash_alg, file_hash, str(file_path)),
		)
		cleanup.callback(self.owner.call, command = "remove.firmware", args = [version, f"make={make}", f"model={model}"])

	def run(self, args):
		params, args = args
		self.validate_args(args = args)
		version = args[0].lower()

		*params_to_lower, hash_value, source = self.owner.fillParams(
			names = [
				("make", ""),
				("model", ""),
				("imp", ""),
				("hosts", ""),
				("hash_alg", "md5"),
				("hash", ""),
				("source", ""),
			],
			params = params,
		)
		# Lowercase all params that can be.
		make, model, imp, hosts, hash_alg = lowered(params_to_lower)
		self.validate_inputs(
			source = source,
			make = make,
			model = model,
			version = version,
			imp = imp,
			hash_alg = hash_alg,
		)

		# Convert hosts to a list if set
		if hosts:
			# Make sure the host names are unique.
			hosts = tuple(unique_everseen(host.strip() for host in hosts.split(",") if host.strip()))
			# Validate the hosts exist.
			hosts = self.owner.getHosts(args = hosts)

		# we use ExitStack to hold our cleanup operations and roll back should something fail.
		with ExitStack() as cleanup:
			# Get the firmware file on disk in the right location and add the metadata to the database.
			self.add_firmware(
				source = source,
				make = make,
				model = model,
				version = version,
				imp = imp,
				hash_value = hash_value,
				hash_alg = hash_alg,
				cleanup = cleanup,
			)

			# if hosts are provided, set the firmware relation
			if hosts:
				self.owner.call(command = "add.host.firmware.mapping", args = [*hosts, f"version={version}", f"make={make}", f"model={model}"])

			# everything went down without a problem, dismiss the cleanup
			cleanup.pop_all()

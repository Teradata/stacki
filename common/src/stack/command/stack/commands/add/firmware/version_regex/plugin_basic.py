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

import re
from contextlib import ExitStack
from stack.util import unique_everseen
import stack.commands
from stack.exception import ArgError, ArgRequired, ArgUnique, ParamRequired, ParamError

class Plugin(stack.commands.Plugin):
	"""Attempts to add a version_regex to the database and associate it with the specified makes and/or models."""

	def provides(self):
		return "basic"

	def validate_args(self, args):
		"""Validate that the arguments to this plugin are as expected."""
		# Require a version regex
		if not args:
			raise ArgRequired(cmd = self.owner, arg = "regex")

		# Should only be one
		if len(args) != 1:
			raise ArgUnique(cmd = self.owner, arg = "regex")

	def validate_regex(self, regex):
		"""Make sure the provided regex is a valid Python regex."""
		# Don't allow empty string, which will compile into a regex fine.
		if not regex:
			raise ArgError(
				cmd = self.owner,
				arg = "regex",
				msg = f"Regex cannot be an empty string."
			)

		# Require the version_regex to be a valid regex
		try:
			re.compile(regex)
		except re.error as exception:
			raise ArgError(
				cmd = self.owner,
				arg = "regex",
				msg = f"Invalid regex supplied: {exception}."
			)

	def validate_name(self, name):
		"""Validate the name is provided and is unique."""
		# A name is required
		if not name:
			raise ParamRequired(cmd = self.owner, param = "name")

		# The name must not already exist
		if self.owner.version_regex_exists(name = name):
			raise ParamError(
				cmd = self.owner,
				param = "name",
				msg = f"A version_regex with the name {name} already exists in the database."
			)

	def run(self, args):
		params, args = args
		self.validate_args(args = args)
		version_regex = args[0]
		self.validate_regex(regex = version_regex)

		name, description, make, models = self.owner.fillParams(
			names = [
				("name", ""),
				("description", ""),
				("make", ""),
				("models", ""),
			],
			params = params,
		)
		name = name.lower()
		self.validate_name(name = name)
		make = make.lower()
		models = models.lower()
		# Process models if specified
		if models:
			models = tuple(
				unique_everseen(
					(model.strip() for model in models.split(',') if model.strip())
				)
			)
			# The make and models must exist
			self.owner.ensure_models_exist(make = make, models = models)
		else:
			# Only need to check that the make exists.
			self.owner.ensure_make_exists(make = make)

		with ExitStack() as cleanup:
			# add the regex
			self.owner.db.execute(
				"""
				INSERT INTO firmware_version_regex (
					regex,
					name,
					description
				)
				VALUES (%s, %s, %s)
				""",
				(version_regex, name, description),
			)
			cleanup.callback(self.owner.call, command = "remove.firmware.version_regex", args = [name])

			# If models are specified, associate it with the relevant models for the given make
			if models:
				self.owner.call(
					command = "set.firmware.model.version_regex",
					args = [*models, f"make={make}", f"version_regex={name}"],
				)
			# else associate it with just the make
			else:
				self.owner.call(
					command = "set.firmware.make.version_regex",
					args = [make, f"version_regex={name}"],
				)

			# everything worked, dismiss cleanup
			cleanup.pop_all()

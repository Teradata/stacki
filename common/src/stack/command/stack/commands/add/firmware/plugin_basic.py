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
from pathlib import Path
from contextlib import ExitStack

class Plugin(stack.commands.Plugin):
	"""Attempts to add firmware to be tracked by stacki."""
	BASE_PATH = Path('/export/stack/firmware/')
	SUPPORTED_SCHEMES = ('file',)

	def provides(self):
		return 'basic'

	def validate_arguments(self, version, params):
		"""Validates that the expected arguments are present and that the optional arguments are specified correctly (if at all).

		Returns the validated arguments if all checks are successful
		"""
		source, make, model, hash_value, hash_alg = params
		# Require a version name
		if not version:
			raise ArgRequired(cmd = self.owner, arg = 'version')
		# should only be one version name
		if len(version) != 1:
			raise ArgUnique(cmd = self.owner, arg = 'version')

		# require a source
		if source is None:
			raise ParamRequired(cmd = self.owner, param = 'source')
		# require both make and model
		if make is None:
			raise ParamRequired(cmd = self.owner, param = 'make')
		if model is None:
			raise ParamRequired(cmd = self.owner, param = 'model')
		# require hash_alg to be one of the always present ones
		if hash_alg not in stack.firmware.SUPPORTED_HASH_ALGS:
			raise ParamError(
				cmd = self.owner,
				param = 'hash_alg',
				msg = f'hash_alg must be one of the following: {stack.firmware.SUPPORTED_HASH_ALGS}'
			)

		return (version[0], source, make, model, hash_value, hash_alg)

	def add_related_entries(self, make, model, cleanup):
		"""Adds the related database entries if they do not exist."""
		# create the make if it doesn't already exist
		if not self.owner.make_exists(make = make):
			self.owner.call(command = 'add.firmware.make', args = [make])
			cleanup.callback(lambda: self.owner.call(command = 'remove.firmware.make', args = [make]))

		# create the model if it doesn't already exist
		if not self.owner.model_exists(make = make, model = model):
			self.owner.call(command = 'add.firmware.model', args = [model, f'make={make}'])
			cleanup.callback(lambda: self.owner.call(command = 'remove.firmware.model', args = [model, f'make={make}']))

	def run(self, args):
		params, version = args
		params = self.owner.fillParams(
			names = [
				('source', None),
				('make', None),
				('model', None),
				('hash', None),
				('hash_alg', 'md5')
			],
			params = params
		)
		# validate the args before use
		version, source, make, model, hash_value, hash_alg = self.validate_arguments(
			version = version,
			params = params
		)

		# ensure the firmware version doesn't already exist for the given model
		if self.owner.firmware_exists(make, model, version):
			raise ArgError(
				cmd = self.owner,
				arg = 'version',
				msg = f'The firmware version {version} for make {make} and model {model} already exists.'
			)

		# we use ExitStack to hold our cleanup operations and roll back should something fail.
		with ExitStack() as cleanup:
			# fetch the firmware from the source and copy the firmware into a stacki managed file
			try:
				file_path = stack.firmware.fetch_firmware(
					source = source,
					make = make,
					model = model
				)
				cleanup.callback(file_path.unlink)
			except stack.firmware.FirmwareError as exception:
				raise ParamError(
					cmd = self.owner,
					param = 'source',
					msg = f'{exception}'
				)
			# calculate the file hash and compare it with the user provided value if present.
			try:
				file_hash = stack.firmware.calculate_hash(file_path = file_path, hash_alg = hash_alg, hash_value = hash_value)
			except stack.firmware.FirmwareError as exception:
				raise ParamError(
					cmd = self.owner,
					param = 'hash',
					msg = f'{exception}'
				)

			# add make and model database entries if needed.
			self.add_related_entries(make = make, model = model, cleanup = cleanup)

			# get the ID of the model to associate with
			model_id = self.owner.get_model_id(make, model)
			# insert into DB associated with make + model
			self.owner.db.execute(
				'''
				INSERT INTO firmware (
					model_id,
					source,
					version,
					hash_alg,
					hash,
					file
				)
				VALUES (%s, %s, %s, %s, %s, %s)
				''',
				(model_id, source, version, hash_alg, file_hash, str(file_path))
			)

			# everything went down without a problem, dismiss the cleanup
			cleanup.pop_all()

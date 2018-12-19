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
import hashlib
from pathlib import Path
import uuid
from urllib.parse import urlparse
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
		if hash_alg not in hashlib.algorithms_guaranteed:
			raise ParamError(
				cmd = self.owner,
				param = 'hash_alg',
				msg = f'hash_alg must be one of the following: {hashlib.algorithms_guaranteed}'
			)

		return (version[0], source, make, model, hash_value, hash_alg)

	def fetch_firmware(self, source, make, model, cleanup):
		"""Fetches the firmware file from the provided source and copies it into a stacki managed file."""
		# parse the URL to figure out how we're going to fetch it
		url = urlparse(url = source)
		if url.scheme not in self.SUPPORTED_SCHEMES:
			raise ParamError(
				cmd = self.owner,
				param = 'source',
				msg = f'source must use one of the following supported schemes: {self.SUPPORTED_SCHEMES}'
			)

		# build file path to write out to
		dest_dir = self.BASE_PATH / make / model
		dest_dir = dest_dir.resolve()
		dest_dir.mkdir(parents = True, exist_ok = True)
		cleanup.callback(dest_dir.rmdir)
		# get a random file name and touch it to create the file
		final_file = dest_dir / uuid.uuid4().hex
		final_file.touch()
		cleanup.callback(final_file.unlink)

		if url.scheme == 'file':
			# grab the source file and copy it into the destination file
			source_file = Path(url.path).resolve(strict = True)
			final_file.write_bytes(source_file.read_bytes())
		# add more supported schemes here
		# elif url.scheme == 'some_other_supported_scheme':

		return final_file

	def calculate_hash(self, file_path, hash_alg, hash_value = None):
		"""Calculates the hash of the provided file using the provided algorithm and returns it as a hex string.

		If a hash value is provided, this checks the calculated hash against the provided hash.
		"""
		calculated_hash = hashlib.new(name = hash_alg, data = file_path.read_bytes()).hexdigest()
		if hash_value is not None and hash_value != calculated_hash:
			raise ParamError(
				cmd = self.owner,
				param = 'hash',
				msg = f'Calculated hash {calculated_hash} does not match provided hash {hash_value}. Algorithm was {hash_alg}.'
			)

		return calculated_hash

	def add_related_entries(self, make, model, cleanup):
		"""Adds the related database entries if they do not exist."""

		# create the make if it doesn't already exist
		if not self.owner.db.count('(id) FROM firmware_make WHERE name=%s', make):
			self.owner.call(command = 'add.firmware.make', args = [make])
			cleanup.callback(lambda: self.owner.call(command = 'remove.firmware.make', args = [make]))

		# create the model if it doesn't already exist
		if not self.owner.db.count(
			'''
			(firmware_model.id)
			FROM firmware_model
				INNER JOIN firmware_make
					ON firmware_model.make_id=firmware_make.id
			WHERE firmware_model.name=%s AND firmware_make.name=%s
			''',
			(model, make)
		):
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
		if self.owner.db.count(
			'''
			(firmware.id)
			FROM firmware
				INNER JOIN firmware_model
					ON firmware.model_id=firmware_model.id
				INNER JOIN firmware_make
					ON firmware_model.make_id=firmware_make.id
			WHERE firmware.version=%s AND firmware_make.name=%s AND firmware_model.name=%s
			''',
			(version, make, model)
		):
			raise ArgError(cmd = self.owner, arg = 'version', msg = f'The firmware version {version} for make {make} and model {model} already exists.')

		# we use ExitStack to hold our cleanup operations and roll back should something fail.
		with ExitStack() as cleanup:
			# fetch the firmware from the source and copy the firmware into a stacki managed file
			file_path = self.fetch_firmware(
				source = source,
				make = make,
				model = model,
				cleanup = cleanup
			)
			# calculate the file hash and compare it with the user provided value if present.
			file_hash = self.calculate_hash(file_path = file_path, hash_alg = hash_alg, hash_value = hash_value)
			# add make and model database entries if needed.
			self.add_related_entries(make = make, model = model, cleanup = cleanup)

			# get the ID of the model to associate with
			model_id = self.owner.db.select('(id) FROM firmware_model WHERE name=%s', model)[0][0]
			# get the ID of the model to associate with
			model_id = self.owner.db.select(
				'''
				firmware_model.id
				FROM firmware_model
					INNER JOIN firmware_make
						ON firmware_model.make_id=firmware_make.id
				WHERE firmware_make.name=%s AND firmware_model.name=%s
				''',
				(make, model)
			)[0][0]
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

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

from pathlib import Path
from urllib.parse import urlparse
import hashlib
import uuid
import stack.commands
from stack.exception import ArgError, ParamRequired, ParamError, CommandError
from stack.util import flatten

class Plugin(stack.commands.Plugin):
	"""Attempts to sync firmware files on the filesystem with what is in the stacki database"""
	BASE_PATH = Path('/export/stack/firmware/')
	SUPPORTED_SCHEMES = ('file',)

	def fetch_firmware(self, source, make, model, filename = None, cleanup = None):
		"""Fetches the firmware file from the provided source and copies it into a stacki managed file."""
		# parse the URL to figure out how we're going to fetch it
		url = urlparse(url = source)

		# build file path to write out to
		dest_dir = self.BASE_PATH / make / model
		dest_dir = dest_dir.resolve()
		dest_dir.mkdir(parents = True, exist_ok = True)
		# set a random file name if the name is not set and touch it to create the file
		final_file = dest_dir / (uuid.uuid4().hex if filename is None else filename)
		final_file.touch()
		if cleanup is not None:
			cleanup.callback(final_file.unlink)

		# copy from local file
		if url.scheme == self.SUPPORTED_SCHEMES[0]:
			# grab the source file and copy it into the destination file
			try:
				source_file = Path(url.path).resolve(strict = True)
			except FileNotFoundError as exception:
				raise ParamError(cmd = self.owner, param = 'source', msg = f'{exception}')

			final_file.write_bytes(source_file.read_bytes())
		# add more supported schemes here
		# elif url.scheme == self.SUPPORTED_SCHEMES[N]:
		else:
			raise ParamError(
				cmd = self.owner,
				param = 'source',
				msg = f'source must use one of the following supported schemes: {self.SUPPORTED_SCHEMES}'
			)

		return final_file

	def calculate_hash(self, file_path, hash_alg, hash_value = None):
		"""Calculates the hash of the provided file using the provided algorithm and returns it as a hex string.

		If a hash value is provided, this checks the calculated hash against the provided hash.
		"""
		calculated_hash = hashlib.new(name = hash_alg, data = Path(file_path).read_bytes()).hexdigest()
		if hash_value is not None and hash_value != calculated_hash:
			raise ParamError(
				cmd = self.owner,
				param = 'hash',
				msg = f'Calculated hash {calculated_hash} does not match provided hash {hash_value}. Algorithm was {hash_alg}.'
			)

		return calculated_hash

	def provides(self):
		return 'basic'

	def run(self, args):
		params, args = args
		make, model = self.owner.fillParams(
			names = [
				('make', None),
				('model', None)
			],
			params = params
		)
		# get rid of any duplicate names
		versions = self.owner.remove_duplicates(args)

		if versions:
			# if versions were provided, require a make and model
			if make is None:
				raise ParamRequired(cmd = self.owner, param = 'make')
			if model is None:
				raise ParamRequired(cmd = self.owner, param = 'model')
			# ensure the versions exist in the DB
			try:
				self.owner.validate_firmwares_exist(make = make, model = model, versions = versions)
			except CommandError as exception:
				raise ArgError(
					cmd = self.owner,
					arg = 'version',
					msg = exception.message()
				)
			# check the files for the versions specified
			for row in self.owner.db.select(
				'''
				firmware.source, firmware.hash_alg, firmware.hash, firmware.file
				FROM firmware
					INNER JOIN firmware_model
						ON firmware.model_id=firmware_model.id
					INNER JOIN firmware_make
						ON firmware_model.make_id=firmware_make.id
				WHERE firmware.version IN %s AND firmware_make.name=%s AND firmware_model.name=%s
				''',
				(versions, make, model)
			):
				source, hash_alg, hash_value, local_file = row
				# check that the local file exists, and fetch it if not
				if not Path(local_file).exists():
					local_file = self.fetch_firmware(source = source, make = make, model = model, filename = local_file.name)
				# verify the hash
				self.calculate_hash(file_path = local_file, hash_alg = hash_alg, hash_value = hash_value)

		else:
			for row in self.owner.db.select(
				'''
				firmware.source, firmware.hash_alg, firmware.hash, firmware.file, firmware_make.name, firmware_model.name
				FROM firmware
					INNER JOIN firmware_model
						ON firmware.model_id=firmware_model.id
					INNER JOIN firmware_make
						ON firmware_model.make_id=firmware_make.id
				'''
			):
				source, hash_alg, hash_value, local_file, make, model = row
				local_file = Path(local_file)
				# check that the local file exists, and fetch it if not
				if not local_file.exists():
					local_file = self.fetch_firmware(source = source, make = make, model = model, filename = local_file.name)
				# verify the hash
				self.calculate_hash(file_path = local_file, hash_alg = hash_alg, hash_value = hash_value)

		# prune any files that shouldn't be there
		files_expected = [
			Path(file_path).resolve(strict = True)
			for file_path in flatten(self.owner.db.select('firmware.file FROM firmware'))
		]
		for file_path in self.BASE_PATH.glob('**/*'):
			file_path = file_path.resolve(strict = True)
			if file_path.is_file() and file_path not in files_expected:
				file_path.unlink()

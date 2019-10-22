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
import stack.commands
import stack.firmware
from stack.util import unique_everseen
from stack.exception import ArgError, ParamRequired, CommandError

class Plugin(stack.commands.Plugin):
	"""Attempts to sync firmware files on the filesystem with what is in the stacki database"""

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
		versions = tuple(unique_everseen(args))
		# set up for a potential where clause
		where_clause = ""
		query_args = tuple()

		if versions:
			# ensure the versions exist in the DB
			self.owner.ensure_firmwares_exist(make = make, model = model, versions = versions)
			# limit query to the selected versions
			where_clause = "WHERE firmware.version IN %s AND firmware_make.name=%s AND firmware_model.name=%s"
			query_args = (versions, make, model)

		for row in self.owner.db.select(
			f'''
			firmware.version, firmware.source, firmware.hash_alg, firmware.hash, firmware.file, firmware_make.name, firmware_model.name
			FROM firmware
				INNER JOIN firmware_model
					ON firmware.model_id=firmware_model.id
				INNER JOIN firmware_make
					ON firmware_model.make_id=firmware_make.id
			{where_clause}
			''',
			query_args,
		):
			version, source, hash_alg, hash_value, local_file, make, model = row
			local_file = Path(local_file)
			# check that the local file exists, and fetch it if not
			if not local_file.exists():
				try:
					local_file = stack.firmware.fetch_firmware(
						source = source,
						make = make,
						model = model,
						filename = local_file.name
					)
				except stack.firmware.FirmwareError as exception:
					raise CommandError(
						cmd = self.owner,
						msg = f'Error while fetching version {version} for make {make} and model {model}: {exception}'
					)
			# verify the hash
			try:
				stack.firmware.calculate_hash(file_path = local_file, hash_alg = hash_alg, hash_value = hash_value)
			except stack.firmware.FirmwareError as exception:
				raise CommandError(
					cmd = self.owner,
					msg = f'Error during file verification: {exception}'
				)

		# prune any files that shouldn't be there
		files_expected = [
			Path(file_path).resolve()
			for file_path in (row[0] for row in self.owner.db.select('firmware.file FROM firmware'))
		]
		for file_path in stack.firmware.BASE_PATH.glob('**/*'):
			file_path = file_path.resolve(strict = True)
			if file_path.is_file() and file_path not in files_expected:
				file_path.unlink()

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
from stack.exception import ArgRequired, ArgError, ParamError, ParamRequired, CommandError
from pathlib import Path

class Plugin(stack.commands.Plugin):
	"""Attempts to remove all provided firmware versions for the given make and model from the database and the file system."""

	def provides(self):
		return 'basic'

	def run(self, args):
		params, args = args
		make, model = self.owner.fillParams(
			names = [('make', None), ('model', None)],
			params = params
		)
		# Require at least one version
		if not args:
			raise ArgRequired(cmd = self.owner, arg = 'version')
		# make and model are required
		if make is None:
			raise ParamRequired(cmd = self.owner, param = 'make')
		if model is None:
			raise ParamRequired(cmd = self.owner, param = 'model')

		# get rid of any duplicate names
		versions = self.owner.remove_duplicates(args)
		# ensure the make and model already exist
		if not self.owner.make_exists(make):
			raise ParamError(
				cmd = self.owner,
				param = 'make',
				msg = f"The firmware make {make} doesn't exist."
			)
		if not self.owner.model_exists(make, model):
			raise ParamError(
				cmd = self.owner,
				param = 'model',
				msg = f"The firmware model {model} for make {make} doesn't exist."
			)
		# ensure the versions exist
		try:
			self.owner.validate_firmwares_exist(make = make, model = model, versions = versions)
		except CommandError as exception:
			raise ArgError(
				cmd = self.owner,
				arg = 'version',
				msg = exception.message()
			)

		# get the firmware to remove
		firmware_to_remove = []
		for version in versions:
			row = self.owner.db.select(
				'''
				firmware.id, firmware.file
				FROM firmware
					INNER JOIN firmware_model
						ON firmware.model_id=firmware_model.id
					INNER JOIN firmware_make
						ON firmware_model.make_id=firmware_make.id
				WHERE firmware.version=%s AND firmware_make.name=%s AND firmware_model.name=%s
				''',
				(version, make, model)
			)[0]
			firmware_to_remove.append((row[0], row[1]))

		# remove the file and then the db entry for each firmware to remove
		for firmware_id, file_path in firmware_to_remove:
			Path(file_path).resolve(strict = True).unlink()
			self.owner.db.execute(
				'''
				DELETE FROM firmware WHERE id=%s
				''',
				firmware_id
			)

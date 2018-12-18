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
from stack.exception import ArgRequired, ArgError, ParamError, ParamRequired
from pathlib import Path

class Plugin(stack.commands.Plugin):
	"""Attempts to remove all provided firmware versions for the given family from the database and the file system."""

	def provides(self):
		return 'basic'

	def run(self, args):
		# Require at least one family name
		params, args = args
		family, = self.owner.fillParams(
			names = [('family', None),],
			params = params
		)
		if not args:
			raise ArgRequired(cmd = self.owner, arg = 'version')

		if family is None:
			ParamRequired(cmd = self.owner, arg = 'family')

		# get rid of any duplicate names
		versions = set(args)
		# ensure the family name already exists
		if not self.owner.db.count('(id) FROM firmware_family WHERE name=%s', family):
			raise ParamError(cmd = self.owner, param = 'family', msg = f"The firmware family {family} doesn't exist.")
		# ensure the versions exist
		missing_versions = [
			version
			for version, count in (
				(
					version,
					self.owner.db.count(
						'''
						(firmware.id)
						FROM firmware
							INNER JOIN firmware_family
								ON firmware.family_id=firmware_family.id
						WHERE firmware.version=%s AND firmware_family.name=%s
						''',
						(version, family)
					)
				)
				for version in versions
			)
			if count == 0
		]
		if missing_versions:
			raise ArgError(
				cmd = self.owner,
				arg = 'version',
				msg = f"The following firmware versions don't exist for family {family}: {missing_versions}."
			)

		# get the firmware to remove
		firmware_to_remove = []
		for version in versions:
			row = self.owner.db.select(
				'''
				firmware.id, firmware.file
				FROM firmware
					INNER JOIN firmware_family
						ON firmware.family_id=firmware_family.id
				WHERE firmware.version=%s AND firmware_family.name=%s
				''',
				(version, family)
			)[0]
			firmware_to_remove.append((row[0], row[1]))

		# remove the file and then the db entry for each firmware to remove
		for firmware_id, file_path in firmware_to_remove:
			Path(file_path).resolve(strict = True).unlink()
			self.owner.db.execute(
				'''
				DELETE FROM firmware_family WHERE id=%s
				''',
				firmware_id
			)

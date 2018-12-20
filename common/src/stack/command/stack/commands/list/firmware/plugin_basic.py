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

class Plugin(stack.commands.Plugin):
	"""Returns information about all firmware versions tracked in the database.

	If expanded is set to True, additional information is returned.
	"""

	def provides(self):
		return 'basic'

	def run(self, args):
		expanded = args
		keys = ['make', 'model', 'version']
		if expanded:
			keys.extend(['source', 'hash', 'hash_alg'])
			values = [
				(row[0], row[1:])
				for row in self.owner.db.select(
					'''
					firmware_make.name, firmware_model.name, firmware.version, firmware.source, firmware.hash, firmware.hash_alg
					FROM firmware
						INNER JOIN firmware_model
							ON firmware.model_id=firmware_model.id
						INNER JOIN firmware_make
							ON firmware_model.make_id=firmware_make.id
					'''
				)
			]
		else:
			values = [
				(row[0], row[1:])
				for row in self.owner.db.select(
					'''
					firmware_make.name, firmware_model.name, firmware.version
					FROM firmware
						INNER JOIN firmware_model
							ON firmware.model_id=firmware_model.id
						INNER JOIN firmware_make
							ON firmware_model.make_id=firmware_make.id
					'''
				)
			]

		return {'keys': keys, 'values': values}

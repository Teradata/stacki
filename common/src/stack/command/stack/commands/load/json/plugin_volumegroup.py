# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import json
from stack.exception import CommandError

class Plugin(stack.commands.Plugin, stack.commands.Command):
	notifications = True

	def provides(self):
		return 'volumegroup'

	def requires(self):
		return [ 'software', 'environment', 'group' ]

	def run(self, args):

		# check if the user would like to import software data
		# if there are no args, assume the user would like to import everthing
		if args and 'volumegroup' not in args:
			return

		# self.owner.data contains the data from the json file defined in init
		if 'volumegroup' in self.owner.data:
			import_data = self.owner.data['volumegroup']
		else:
			self.owner.log.info('no volumegroup data in the json document')
			return

		self.notify('\n\tLoading Volumegroup\n')
		# TODO: sanitize validate
		for volumegroup in import_data:
			array = volumegroup['array'].strip()

			parameters = [
				array,
				f'disks={volumegroup["tray"]}:{volumegroup["slot"]}',
				f'raidlevel={volumegroup["raidlevel"]}',
				f'volumegroup={volumegroup["volumegroup"]}',
				f'options={volumegroup["options"]}'
			]
			self.owner.try_command('add.netapp.array.volumegroup', parameters, f'adding volumegroup for the array  {array}', 'exists')


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
		return 'controller'

	def requires(self):
		return [ 'software', 'environment', 'group' ]

	def run(self, args):

		# check if the user would like to import software data
		# if there are no args, assume the user would like to import everthing
		if args and 'controller' not in args:
			return

		# self.owner.data contains the data from the json file defined in init
		if 'controller' in self.owner.data:
			import_data = self.owner.data['controller']
		else:
			self.owner.log.info('no controller data in the json document')
			return

		self.notify('\n\tLoading Controller\n')
		# TODO: sanitize validate
		for controller in import_data:
			array = controller['array'].strip()

			parameters = [
				array,
				f'controller={controller["controller"]}',
				f'mac={controller["mac"]}'
			]

			if "=" in controller["options"]:
				parameters.append(f'options={controller["options"]}')

			self.owner.try_command('add.netapp.array.controller', parameters, f'adding controller for the array  {array}', 'exists')


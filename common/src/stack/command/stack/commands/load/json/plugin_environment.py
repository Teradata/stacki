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
		return 'environment'
	def requires(self):
		return [ 'software' ]

	def run(self, args):

		# check if the user would like to import environment data
		# if there are no args, assume the user would like to import everthing
		if args and 'environment' not in args:
			return

		# self.owner.data contains the data from the json file defined in init
		if 'environment' in self.owner.data:
			import_data = self.owner.data['environment']
		else:
			self.owner.log.info('no environment data in json file')
			return

		self.notify('\n\tLoading environment\n')
		for environment in import_data:
			environment_name= environment['name']
			self.owner.try_command('add.environment', [ environment_name ] , f'adding environment {environment_name}', 'exists')

			for attr in environment['attrs']:
				# determine if this is a shadow attr by looking at the type
				if attr['type'] == 'shadow':
					attr_shadow = True
				else:
					attr_shadow = False
				parameters = [
					environment_name,
					f'attr={attr["attr"]}',
					f'value={attr["value"]}',
					f'shadow={attr_shadow}'
					]

				self.owner.try_command('add.environment.attr', parameters, f'adding environment attr {attr}', 'exists')

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
			try:
				self.owner.command('add.environment', [ environment_name ])
			except CommandError as e:
				if 'exists' in str(e):
					self.owner.log.info(f'warning adding environment {environment_name}: {e}')
					self.owner.warnings += 1
				else:
					self.owner.log.info(f'error adding environment {environment}: {e}')
					self.owner.errors += 1

			for attr in environment['attrs']:
				#determine if this is a shadow attr by looking at the type
				if attr['type'] == 'shadow':
					attr_shadow = True
				else:
					attr_shadow = False
				try:
					self.owner.command('add.environment.attr', [
							environment_name,
							f'attr={attr["attr"]}',
							f'value={attr["value"]}',
							f'shadow={attr_shadow}'
					])
					self.owner.successes += 1

				except CommandError as e:
					if 'exists' in str(e):
						self.owner.log.info(f'warning adding environment attr {attr}: {e}')
						self.owner.warnings += 1
					else:
						self.owner.log.info(f'error adding environment attr {attr}: {e}')
						self.owner.errors += 1

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
		return 'bootaction'

	def requires(self):
		return [ 'software', 'environment', 'group', 'network', 'appliance', 'os', 'global', 'host' ]

	def run(self, args):

		# check if the user would like to import bootaction data
		# if there are no args, assume the user would like to import everthing
		if args and 'bootaction' not in args:
			return

		# self.owner.data contains the data from the json file defined in init
		if 'bootaction' in self.owner.data:
			import_data = self.owner.data['bootaction']
		else:
			self.owner.log.info('no bootaction data in json file')
			return

		self.notify('\n\tLoading bootaction\n')

		for profile in import_data:
			action = profile['name']

			parameters = [
				action,
				f'kernel={profile["kernel"]}',
				f'type={profile["type"]}'
			]
			if profile['os']:
				parameters.append(f'os={profile["os"]}')
			if profile['ramdisk']:
				parameters.append(f'ramdisk={profile["ramdisk"]}')

			self.owner.try_command('set.bootaction',parameters , f'adding bootaction {action}', 'exists')
			# in the event that the bootaction already exists but with different args,
			# we replace the old args with the new by setting them
			if profile['args']:
				args = ' '.join(profile['args'])
				parameters = [action, f'args={args}', f'type={profile["type"]}']
				if profile['os']:
					parameters.append(f'os={profile["os"]}')
				self.owner.try_command('set.bootaction.args', parameters , f'adding bootaction {action} args', 'exists')

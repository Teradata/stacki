# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import json

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'bootaction'

	def run(self, args):

		#check if the user would like to import bootaction data
		#if there are no args, assume the user would like to import everthing
		if args and 'bootaction' not in args:
			return

		#self.owner.data contains the data from the json file defined in init
		#check if there is any bootaction data before we go getting all kinds of key errors
		if 'bootaction' in self.owner.data:
			import_data = self.owner.data['bootaction']
		else:
			print('no bootaction data in json file')
			return


		for profile in import_data:
			action = profile['name']

			command = [action,
					f'kernel={profile["kernel"]}',
					f'type={profile["type"]}']
			if profile['os']:
				command.append(f'os={profile["os"]}')
			if profile['ramdisk']:
				command.append(f'ramdisk={profile["ramdisk"]}')

			#Need to make a more specific try catch
			try:
				self.owner.command('add.bootaction', command )
				print(f'success importing bootaction {action}')
				self.owner.successes += 1

			except Exception as e:
				if 'exists' in str(e):
					print(f'warning importing bootaction {action}: {e}')
					self.owner.warnings += 1
				else:
					print(f'error importing bootaction {action}: {e}')
					self.owner.errors += 1

			#on occasion, not all of the args will be added if they are included in the original command
			#to remedy this we set the args after adding the bootaction profile
			if profile['args']:
				args = ' '.join(profile['args'])
				command = [action, f'args={args}', f'type={profile["type"]}']
				if profile['os']:
					command.append(f'os={profile["os"]}')
				try:
					self.owner.command('set.bootaction.args', command)
					print(f'success setting bootaction {action} args')
					self.owner.successes += 1
				except Exception as e:
					if 'exists' in str(e):
						print(f'warning setting bootaction {action} args: {e}')
						self.owner.warnings += 1
					else:
						print(f'error setting bootaction {action} args: {e}')
						self.owner.errors += 1

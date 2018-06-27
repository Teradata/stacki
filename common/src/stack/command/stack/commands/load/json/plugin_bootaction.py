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
			args = str(profile['args']).strip("['']")
			kernel = profile['kernel'] 
			os = profile['os']
			ramdisk = profile['ramdisk']
			boot_action_type = profile['type']

			
			#Need to make a more specific try catch
			try:
				#if there is no os, leaving it blank will make the scope global
				if os == None:		
					results = self.owner.command('add.bootaction', [f'"{action}"', f'args="{args}"', f'kernel="{kernel}"',
							f'ramdisk={ramdisk}', f'type={boot_action_type}'])
				else: 
					results = self.owner.command('add.bootaction', [f'"{action}"', f'args="{args}"', f'kernel="{kernel}"',
							f'os={os}', f'ramdisk={ramdisk}', f'type={boot_action_type}'])
				self.owner.successes += 1
		
			except Exception as e:
				if 'exists' in str(e):
					print(f'warning importing bootaction {action}: {e}')
					self.owner.warnings += 1
				else:
					print(f'error importing bootaction {action}: {e}')
					self.owner.errors += 1


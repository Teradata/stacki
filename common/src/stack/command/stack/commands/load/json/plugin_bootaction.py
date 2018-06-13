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
		if args:
			if 'bootaction' not in args:
				return

		#self.owner.data contains the data from the json file defined in init
		for item in self.owner.data:
			if item == 'bootaction':
				import_data = self.owner.data[item]
			else:
				print('error no bootaction data in json file')
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
				print('add.bootaction', f'"{action}"', f'args={args}', f'kernel="{kernel}"',
                                                                f'os={os}', f'ramdisk={ramdisk}', f'type={boot_action_type}')
		
		

				if os == None:		
					results = self.owner.command('add.bootaction', [f'"{action}"', f'args="{args}"', f'kernel="{kernel}"',
							f'ramdisk={ramdisk}', f'type={boot_action_type}'])
				else: 
					results = self.owner.command('add.bootaction', [f'"{action}"', f'args="{args}"', f'kernel="{kernel}"',
							f'os={os}', f'ramdisk={ramdisk}', f'type={boot_action_type}'])
		
			except:
				print(f'error importing {action}')

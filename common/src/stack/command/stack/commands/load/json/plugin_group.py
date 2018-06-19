# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import json

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'group'

	def run(self, args):

		#check if the user would like to import group data
		#if there are no args, assume the user would like to import everthing
		if args and 'group' not in args:
			return

		#self.owner.data contains the data from the json file defined in init
		#check if there is any group data before we go getting all kinds of key errors
		if 'group' in self.owner.data:
			import_data = self.owner.data['group']
		else:
			print('no group data in json file')
			return


		for group in import_data:
			try:
				self.owner.command('add.group', [ group['name'] ])
			except Exception as e:
				if 'exists' in str(e):
					print(f'warning adding group {group["name"]}: {e}')
				else:
					print(f'error adding group {group["name"]}: {e}')


RollName="Stacki"

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
		return 'group'

	def requires(self):
		return [ 'software', 'environment' ]

	def run(self, args):

		# check if the user would like to import group data
		# if there are no args, assume the user would like to import everthing
		if args and 'group' not in args:
			return

		# self.owner.data contains the data from the json file defined in init
		if 'group' in self.owner.data:
			import_data = self.owner.data['group']
		else:
			self.owner.log.info('no group data in json file')
			return

		self.notify('\n\tLoading group\n')
		for group in import_data:
			self.owner.try_command('add.group', [ group['name'] ], f'adding group {group["name"]}', 'exists')

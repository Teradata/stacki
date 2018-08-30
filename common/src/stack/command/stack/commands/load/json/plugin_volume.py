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
		return 'volume'

	def requires(self):
		return [ 'software', 'environment', 'group' ]

	def run(self, args):

		# check if the user would like to import software data
		# if there are no args, assume the user would like to import everthing
		if args and 'volume' not in args:
			return

		# self.owner.data contains the data from the json file defined in init
		if 'volume' in self.owner.data:
			import_data = self.owner.data['volume']
		else:
			self.owner.log.info('no volume data in the json document')
			return

		self.notify('\n\tLoading Volume\n')
		# TODO: sanitize validate
		for volume in import_data:
			array = volume['array'].strip()

			parameters = [
				array,
				f'volumegroup={volume["volumegroup"]}',
				f'volumename={volume["volumename"]}',
				f'size={volume["size"]}',
				f'controller={volume["controllerid"]}'
			]

			if volume["options"]:
				parameters.append(f'options={volume["options"]}')
			
			if volume["hostgroup"]:
				parameters.append(f'hostgroup={volume["hostgroup"]}')

			self.owner.try_command('add.netapp.array.volume', parameters, f'adding volume for the array  {array}', 'exists')


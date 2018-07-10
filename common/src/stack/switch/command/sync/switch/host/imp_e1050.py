# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Implementation(stack.commands.Implementation):
	# not really a sync; just placed here for now
	def run(self, args):
		switch_name = args[0]
		lsm = self.owner.call('list.switch.mac', ['pinghosts=True'])  # already sorted?

		self.owner.call('remove.switch.host', [switch_name])  # check success?

		for item in lsm:
			self.owner.call('add.switch.host', [switch_name, f'host={item["host"]}', f'port={item["port"]}', f'interface={item["interface"]}'])


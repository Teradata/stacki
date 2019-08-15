# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'os'

	def run(self, section):

		self.owner.set_scope('os')

		for os in section:
			os_name = os.get('name')

			self.owner.load_attr(os.get('attr'), os_name)
			self.owner.load_controller(os.get('controller'), os_name)
			self.owner.load_partition(os.get('partition'), os_name)
			self.owner.load_firewall(os.get('firewall'), os_name)
			self.owner.load_route(os.get('route'), os_name)

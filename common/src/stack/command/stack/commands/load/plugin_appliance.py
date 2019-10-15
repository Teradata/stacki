# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'appliance'

	def run(self, section):

		self.owner.set_scope('appliance')

		for a in section:
			appliance = a.get('name')
			params    = {'public': a.get('public')}

			self.owner.stack('add.appliance', appliance, **params)

			self.owner.load_attr(a.get('attr'), appliance)
			self.owner.load_controller(a.get('controller'), appliance)
			self.owner.load_partition(a.get('partition'), appliance)
			self.owner.load_firewall(a.get('firewall'), appliance)
			self.owner.load_route(a.get('route'), appliance)





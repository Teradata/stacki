# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'environment'

	def run(self, section):

		self.owner.set_scope('environment')

		for environment in section:
			environment_name = environment.get('name')

			self.owner.stack('add.environment', environment_name)

			self.owner.load_attr(environment.get('attr'), environment_name)
			self.owner.load_controller(environment.get('controller'), environment_name)
			self.owner.load_partition(environment.get('partition'), environment_name)
			self.owner.load_firewall(environment.get('firewall'), environment_name)
			self.owner.load_route(environment.get('route'), environment_name)

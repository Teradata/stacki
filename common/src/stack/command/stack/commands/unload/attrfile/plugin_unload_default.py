# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


import stack.commands
from stack.commands import ApplianceArgProcessor

class Plugin(ApplianceArgProcessor, stack.commands.Plugin):

	def provides(self):
		return 'default'

	def run(self, attrs):
		appliances = self.getApplianceNames()

		for target in attrs.keys():
			if target == 'global':
				cmd = 'remove.attr'
			elif target in appliances:
				cmd = 'remove.appliance.attr'
			else:
				cmd = 'remove.host.attr'

			for attr in attrs[target].keys():
				if target == 'global':
					cmdargs = []
				else:
					cmdargs = [ target ]
				cmdargs.append('attr=%s' % attr)

				self.owner.command(cmd, cmdargs)


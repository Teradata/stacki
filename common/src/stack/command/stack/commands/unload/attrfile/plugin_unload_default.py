# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@


import stack.commands


class Plugin(stack.commands.ApplianceArgumentProcessor, stack.commands.Plugin):

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


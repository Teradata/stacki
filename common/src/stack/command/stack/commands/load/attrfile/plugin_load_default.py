# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@

import stack.commands
from stack.commands import ApplianceArgProcessor, HostArgProcessor

class Plugin(ApplianceArgProcessor, HostArgProcessor, stack.commands.Plugin):

	def provides(self):
		return 'default'

	def run(self, attrs):
		appliances = self.getApplianceNames()
		hosts      = self.getHostnames()

		# Clear out all the attributes represented in the spreadsheet.
		# This prepare us for the next step of adding only the cells 
		# with set values.

		for target in attrs.keys():
			if target == 'default':
				continue
			elif target == 'global':
				if 'environment' not in attrs[target]:
					cmd = 'remove.attr'
					arg = None
				else:
					cmd = 'remove.environment.attr'
					arg = attrs[target]['environment']
			elif target in appliances:
				cmd = 'remove.appliance.attr'
				arg = target
			else:
				cmd = 'remove.host.attr'
				arg = target

			for attr in attrs[target].keys():
				if arg:
					args = [ arg ]
				else:
					args = []
				args.append('attr=%s' % attr)
				self.owner.call(cmd, args)

		#
		# now add the attributes
		#
		for target in attrs.keys():
			if target == 'default':
				continue
			elif target == 'global':
				if 'environment' not in attrs[target]:
					cmd = 'set.attr'
					arg = None
				else:
					cmd = 'set.environment.attr'
					arg = attrs[target]['environment']
			elif target in appliances:
				cmd = 'set.appliance.attr'
				arg = target
			else:
				cmd = 'set.host.attr'
				arg = target

			for attr in attrs[target].keys():
				#
				# only add attributes that have a value
				#
				if not attrs[target][attr]:
					continue
				if arg:
					args = [ arg ]
				else:
					args = []
				args.append('attr=%s' % attr)
				args.append('value=%s' % attrs[target][attr])

				self.owner.call(cmd, args)

			# If the environment is set move all the hosts
			# to an environment specific box.

			box = attrs[target].get('environment')
			if box:
				if target in hosts:
					self.owner.call('set.host.box',
						[ target, 'box=%s' % box ])


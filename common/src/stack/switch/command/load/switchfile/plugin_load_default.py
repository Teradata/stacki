# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@

import sys
import stack.commands
from stack.bool import str2bool


class Plugin(stack.commands.HostArgumentProcessor, stack.commands.Plugin):

	def provides(self):
		return 'default'

	def run(self, args):
		switches = args
		existinghosts = self.getHostnames()

		sys.stderr.write('\tAdd Host\n')
		for switch in switches.keys():

			sys.stderr.write('\t\t%s\r' % switch)

			name		= switches[switch].get('switch')
			model		= switches[switch].get('model')
			ip		= switches[switch].get('ip')
			mac		= switches[switch].get('mac')
			interface	= switches[switch].get('interface')
			rack		= switches[switch].get('rack')
			rank		= switches[switch].get('rank')
			network		= switches[switch].get('network')
			username	= switches[switch].get('username')
			password	= switches[switch].get('password')

			#
			# add the switch if it does exist
			#
			if switch not in existinghosts:
				# add switch
				switch_args = [switch, 
						"model=%s" % model, 
						]

				# add optional arguments if they exist
				if username:
					switch_args.append("username=%s" % username)
				if password:
					switch_args.append("password=%s" % password)
				if rack:
					switch_args.append("rack=%s" % rack)
				if rank:
					switch_args.append("rank=%s" % rank)

				self.owner.command('add.switch', switch_args)

			# Remove old interfaces
			self.owner.command('remove.host.interface', [switch, "all=true"])

			# add interface
			interface_args = [switch, 
					"interface=%s" % interface, 
					"ip=%s" % ip,
					"mac=%s" % mac,
					"network=%s" % network,
					]

			self.owner.command('add.switch.interface', interface_args)

			sys.stderr.write('\t\t%s\r' % (' ' * len(switch)))


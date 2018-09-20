# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'version'

	def requires(self):
		return ['basic']

	def run(self, args):
		(hosts, expanded, hashit) = args

		host_info = dict.fromkeys(hosts)

		for host in hosts:
			appliance = self.owner.call('list.host', [host])[0]['appliance']
			host_info[host] = self.owner.runImplementation(appliance,[host])

		return {'keys'  : ['Current Version','Available Version'],
			'values': host_info }

RollName = "stacki"

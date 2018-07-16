#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import stack.commands

class Implementation(stack.commands.Implementation):
	def run(self, args):
		(switch, hosts) = args

		list_switch_mac = self.owner.call('list.switch.mac', [ switch, 'pinghosts=network' ])

		for h in self.owner.call('list.host.interface', hosts):
			if h['interface'] == 'ipmi':
				continue

			for m in list_switch_mac:
				if h['host'] == m['host'] and h['interface'] == m['interface']:
					params = [ switch, 'host=%s' % h['host'],
						'interface=%s' % m['interface'],
						'port=%s' % m['port'] ]
					self.owner.call('add.switch.host', params)
					break


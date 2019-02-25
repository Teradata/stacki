# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Implementation(stack.commands.Implementation):
	def run(self, args):
		host = args[0]

		self.owner.addOutput(
			host, '<stack:file stack:name="/etc/sysconfig/network/routes">'
		)

		for route in self.owner.call('list.host.route', [host]):
			network = route['network']
			netmask = route['netmask']

			# If interface is not set, use the default behavior
			interface = route['interface']
			if not interface:
				interface = '-'

			gateway = route['gateway']
			if not gateway:
				gateway = '-'

			self.owner.addOutput(host, f'{network}\t{gateway}\t{netmask}\t{interface}')

		# The interface that is designated as the default interface,
		# will be specified as the default route
		for o in self.owner.call('list.host.interface', [host]):
			if o['default']:
				network = o['network']
				device = o['interface'].split(':')[0]

				for n in self.owner.call('list.network', [network]):
					gateway = n['gateway']

					self.owner.addOutput(
						host, f'default\t{gateway}\t0.0.0.0\t{device}'
					)
					break

				break

		self.owner.addOutput(host, '</stack:file>')

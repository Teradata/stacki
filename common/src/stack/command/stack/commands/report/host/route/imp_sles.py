# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands

#
# all global routes go in:
#
#	/etc/sysconfig/network/routes
#
# all interface-specific routes go in:
#
#	/etc/sysconfig/network/ifroute-<interface name>
#


class Implementation(stack.commands.Implementation):
	def run(self, args):

		host = args[0]

		#
		# global routes for the host
		#
		self.owner.addOutput(host, '<stack:file stack:name="/etc/sysconfig/network/routes">')


		routes = self.db.getHostRoutes(host)
		for network in sorted(routes.keys()):
			(netmask, gateway, interface) = routes[network]
			destination = network

			
			# if interface is not set, use the default behavior
			if not interface or interface == 'NULL':
				device = gateway
				gateway = '0.0.0.0'
				self.owner.addOutput(host, '%s\t%s\t%s\t%s' %
					(destination, gateway, netmask, device))

			else:
				device = interface
				self.owner.addOutput(host, '%s\t%s\t%s\t%s' %
					(destination, gateway, netmask, device))
				

		#
		# the interface that is designated as the default interface,
		# will be specified as the default route
		#
		gateway = '0.0.0.0'
		result = self.owner.call('list.host.interface', [ host ])
		for o in result:
			if o['default']: 
				network = o['network']
				device = o['interface']
				destination = 'default'
				netmask = '0.0.0.0'

				output = self.owner.call('list.network',
					[ network ])
				for n in output:
					gateway = n['gateway']

					self.owner.addOutput(host, '%s\t%s\t%s\t%s' % (destination, gateway, netmask, device))
					break

				break
				
		self.owner.addOutput(host, '</stack:file>')

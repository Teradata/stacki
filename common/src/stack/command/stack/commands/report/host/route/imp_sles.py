# @SI_Copyright@
# @SI_Copyright@


import os
import sys
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

		gateway = '0.0.0.0'

		result = self.owner.call('list.host.route', [ host ])
		for o in result:
			destination = o['network']
			netmask = o['netmask']
			device = o['gateway']

			self.owner.addOutput(host, '%s\t%s\t%s\t%s' %
				(destination, gateway, netmask, device))
			break

		#
		# the interface that is designated as the default interface,
		# will be specified as the default route
		#
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

		#
		# add interface specific routes
		#
		network = None
		device = None

		result = self.owner.call('list.host.interface', [ host ])
		for o in result:
			network = o['network']
			device = o['interface']

			if not o['default'] and network and device != 'ipmi': 

				self.owner.addOutput(host, '<stack:file stack:name="/etc/sysconfig/network/ifroute-%s">' % device)

				for row in self.owner.call('list.network', [ network ]):
					destination = row['address']
					gateway	    = row['gateway']
					netmask	    = row['mask']

					self.owner.addOutput(host, '%s\t%s\t%s\t%s' % (destination, gateway, netmask, device))

				self.owner.addOutput(host, '</stack:file>')

				self.owner.addOutput(host, '__EOF__')
				break


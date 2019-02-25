# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Implementation(stack.commands.Implementation):
	def getRoute(self, network, netmask, gateway, interface):
		s = 'any '

		# Is the a host or network route?
		if netmask == '255.255.255.255':
			s += 'host %s ' % network
		else:
			s += 'net %s netmask %s ' % (network, netmask)

		# Is this a gateway or device route?
		if gateway and gateway.count('.') == 3:
			s += 'gw %s' % gateway

			if interface:
				s += ' dev %s' % interface
		else:
			s += 'dev %s' % interface

		return s

	def run(self, args):
		host = args[0]

		self.owner.addOutput(host, '<stack:file stack:name="/etc/sysconfig/static-routes">')

		for route in self.owner.call('list.host.route', [host]):
			# Skip the default route (reported elsewhere)
			if route['network'] != '0.0.0.0':
				self.owner.addOutput(host, self.getRoute(
					route['network'],
					route['netmask'],
					route['gateway'],
					route['interface']
				))

		self.owner.addOutput(host, '</stack:file>')

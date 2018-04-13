# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Implementation(stack.commands.Implementation):

	def getRoute(self, network, netmask, gateway, interface):

		s = 'any '

		# Skip the default route (reported elsewhere)
		
		if network == '0.0.0.0':
			return None
			
		# Is the a host or network route?
				
		if netmask == '255.255.255.255':
			s += 'host %s ' % network
		else:
			s += 'net %s netmask %s ' % (network, netmask)
			
		# Is this a gateway or device route?
				
		if gateway.count('.') == 3:
			s += 'gw %s' % gateway

			if interface and interface != 'NULL':
				s += 'dev %s' % interface
		else:
			s += 'dev %s' % gateway
			
		return s
		
	def run(self, args):

		host = args[0]
		self.owner.addOutput(host,
			'<stack:file stack:name="/etc/sysconfig/static-routes">')
		routes = self.owner.db.getHostRoutes(host)
		for network in sorted(routes.keys()):
			(netmask, gateway, interface) = routes[network]

			s = self.getRoute(network, netmask, gateway, interface)
			if s:
				self.owner.addOutput(host, s)
		self.owner.addOutput(host, '</stack:file>')


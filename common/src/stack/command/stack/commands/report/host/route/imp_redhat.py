#
# @SI_COPYRIGHT@
# @SI_COPYRIGHT@
#

import stack.commands


class Implementation(stack.commands.Implementation):

	def getRoute(self, network, netmask, gateway):

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
		else:
			s += 'dev %s' % gateway
			
		return s
		
	def run(self, args):

		host = args[0]
		self.owner.addOutput(host,
			'<stack:file stack:name="/etc/sysconfig/static-routes">')
		routes = self.owner.db.getHostRoutes(host)
		for (key, val) in routes.items():
			s = self.getRoute(key, val[0], val[1])
			if s:
				self.owner.addOutput(host, s)
		self.owner.addOutput(host, '</stack:file>')


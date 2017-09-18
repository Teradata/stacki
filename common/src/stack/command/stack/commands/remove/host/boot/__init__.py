# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands
from stack.exception import ArgRequired


class Command(stack.commands.remove.host.command):
	"""
	Removes the boot configuration for a host

	<arg type='string' name='host' repeat='1'>
	One or more named hosts.
	</arg>
	
	<example cmd='remove host boot compute-0-0'>
	Removes the boot configuration for host compute-0-0.
	</example>

	<example cmd='remove host boot compute-0-0 compute-0-1'>
	Removes the boot configuration for hosts compute-0-0 and
	compute-0-1.
	</example>
	"""
	
	def getHostHexIP(self, host):
		#
		# Get the IP and NETMASK of the host
		#
	
		appliance = self.getHostAttr(host, 'appliance')
		if appliance == 'frontend':
			return []

		hex_ip_list = []
		for row in self.call('list.host.interface', [host, 'expanded=True']):
			ip = row['ip']
			pxe = row['pxe']
			if ip and pxe:
				#
				# Compute the HEX IP filename for the host
				#
				hexstr = ''
				for i in ip.split('.'):
					hexstr += '%02x' % (int(i))

				hex_ip_list.append(hexstr.upper())
		return hex_ip_list

	def run(self, params, args):
		if not len(args):
			raise ArgRequired(self, 'host')

		hosts = self.getHostnames(args)
		self.runPlugins(hosts)

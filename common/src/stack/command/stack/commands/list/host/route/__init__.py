# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@


import sys
import socket
import stack.commands
import string

class Command(stack.commands.list.host.command):
	"""
	List the static routes that are assigned to a host.

	<arg optional='1' type='string' name='host'>
	Host name of machine
	</arg>
	
	<example cmd='list host route compute-0-0'>
	List the static routes assigned to compute-0-0.
	</example>
	"""

	def run(self, params, args):

		self.beginOutput()
		
		for host in self.getHostnames(args):
			routes = self.db.getHostRoutes(host, 1)

			for key in sorted(routes.keys()):		
				self.addOutput(host, 
					(key,
					routes[key][0], 
					routes[key][1], 
					routes[key][2]))

		self.endOutput(header=['host', 
			'network', 'netmask', 'gateway', 'source' ],
			trimOwner=0)


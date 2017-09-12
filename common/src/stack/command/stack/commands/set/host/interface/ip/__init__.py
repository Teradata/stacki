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

import stack.commands
from stack.exception import ParamRequired, ArgUnique


class Command(stack.commands.set.host.command):
	"""
	Sets the IP address for the named interface for one host.

	<arg type='string' name='host' required='1'>
	Host name.
	</arg>
	
	<param type='string' name='interface'>
	Name of the interface.
	</param>

	<param type='string' name='mac'>
	MAC address of the interface.
	</param>

	<param type='string' name='ip' optional='0'>
	IP address
	</param>

	<example cmd='set host interface ip backend-0-0 interface=eth1 ip=192.168.0.10'>
	Sets the IP Address for the eth1 device on host backend-0-0.
	</example>
	"""
	
	def run(self, params, args):
		
		hosts = self.getHostnames(args)
		(ip, interface, mac) = self.fillParams([
			('ip',        None, True),
			('interface', None),
			('mac',       None)
			])

		if not interface and not mac:
			raise ParamRequired(self, ('interface', 'mac'))
		if len(hosts) != 1:
			raise ArgUnique(self, 'host')

		ip   = ip.upper() # null -> NULL
		host = hosts[0]		

		if interface:
			self.db.execute("""
				update networks, nodes set 
				networks.ip=NULLIF('%s','NULL') where
				nodes.name='%s' and networks.node=nodes.id and
				networks.device like '%s'
				""" % (ip, host, interface))
		else:
			self.db.execute("""
				update networks, nodes set 
				networks.ip=NULLIF('%s','NULL') where
				nodes.name='%s' and networks.node=nodes.id and
				networks.mac like '%s'
				""" % (ip, host, mac))


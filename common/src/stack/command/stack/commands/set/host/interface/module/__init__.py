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


import string
import stack.commands
from stack.exception import ParamRequired


class Command(stack.commands.set.host.command):
	"""
	Sets the device module for a named interface. On Linux this will get
	translated to an entry in /etc/modprobe.conf.

	<arg type='string' name='host' repeat='1' optional='1'>
	One or more hosts.
	</arg>
	
	<param type='string' name='interface'>
	Name of the interface.
	</param>

	<param type='string' name='mac'>
	MAC address of the interface.
	</param>

	<param type='string' name='module' optional='0'>
	Module name.
	</param>
	
	<example cmd='set host interface module backend-0-0 interface=eth1 module=e1000'>
	Sets the device module for eth1 to be e1000 on host backend-0-0.
	</example>
	"""
	
	def run(self, params, args):

		(module, interface, mac) = self.fillParams([
			('module',    None, True),
			('interface', None),
			('mac',       None)
			])

		if not interface and not mac:
			raise ParamRequired(self, ('interface', 'mac'))
		
		if string.upper(module) == 'NULL':
			module = 'NULL'

		for host in self.getHostnames(args):
			if interface:
				self.db.execute("""
					update networks, nodes set 
					networks.module=NULLIF('%s','NULL') where
					nodes.name='%s' and networks.node=nodes.id and
					networks.device like '%s'
					""" % (module, host, interface))
			else:
				self.db.execute("""
					update networks, nodes set 
					networks.module=NULLIF('%s','NULL') where
					nodes.name='%s' and networks.node=nodes.id and
					networks.mac like '%s'
					""" % (module, host, mac))


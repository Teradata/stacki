# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands
from stack.exception import ParamRequired


class Command(stack.commands.set.host.command):
	"""
	Sets the network for named interface on one of more hosts. 

	<arg type='string' name='host' repeat='1' optional='0'>
	One or more named hosts.
	</arg>
	
	<param type='string' name='interface'>
	Name of the interface.
	</param>

	<param type='string' name='mac'>
	MAC address of the interface.
	</param>

	<param type='string' name='network' optional='1'>
	The network address of the interface. This is a named network and must be
	listable by the command 'rocks list network'.
	</param>

	<example cmd='set host interface mac backend-0-0 interface=eth1 network=public'>
	Sets eth1 to be on the public network.
	</example>
	"""
	
	def run(self, params, args):

		(network, interface, mac) = self.fillParams([
			('network',   None, True),
			('interface', None),
			('mac',       None)
			])

		if not interface and not mac:
			raise ParamRequired(self, ('interface', 'mac'))

		for host in self.getHostnames(args):
			if interface:
				self.db.execute("""
					update networks net, nodes n 
					set net.subnet=
					(select id from subnets s where s.name='%s')
					where
					n.name='%s' and net.node=n.id and
					net.device like '%s'
					""" % (network, host, interface))
			else:
				self.db.execute("""
					update networks net, nodes n 
					set net.subnet=
					(select id from subnets s where s.name='%s')
					where
					n.name='%s' and net.node=n.id and
					net.mac like '%s'
					""" % (network, host, mac))

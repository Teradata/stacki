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
from stack.exception import *

class Command(stack.commands.set.host.command):
	"""
	Sets the VLAN ID for an interface on one of more hosts. 

	<arg type='string' name='host' repeat='1' optional='1'>
	One or more named hosts.
	</arg>
	
	<param type='string' name='interface'>
	Name of the interface.
	</param>

	<param type='string' name='mac'>
	MAC address of the interface.
	</param>

	<param type='string' name='vlan' optional='0'>
	The VLAN ID that should be updated. This must be an integer and the
	pair 'subnet/vlan' must be defined in the VLANs table.
	</param>
	
	<example cmd='set host interface vlan backend-0-0-0 interface=eth0 vlan=3'>
	Sets backend-0-0-0's private interface to VLAN ID 3.
	</example>
	"""
	
	def run(self, params, args):

		(vlan, interface, mac) = self.fillParams([
			('vlan',      None, True),
			('interface', None),
			('mac',       None)
			])

		if not interface and not mac:
			raise ParamRequired(self, ('interface', 'mac'))
		try:
			vlanid = int(vlan)
		except:
			raise ParamType(self, 'vlan', 'integer')

		for host in self.getHostnames(args):
			if interface:
				self.db.execute("""
					update networks net, nodes n
					set net.vlanid = IF(%d = 0, NULL, %d)
					where net.device like '%s' and
					n.name = '%s' and net.node = n.id
					""" % (vlanid, vlanid, interface, host))
			else:
				self.db.execute("""
					update networks net, nodes n
					set net.vlanid = IF(%d = 0, NULL, %d)
					where net.mac like'%s' and
					n.name = '%s' and net.node = n.id
					""" % (vlanid, vlanid, mac, host))


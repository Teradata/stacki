# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

from collections import defaultdict
import stack.commands
from stack.exception import ArgRequired, CommandError


class Command(stack.commands.set.host.command):
	"""
	Sets the logical interface of a mac address for particular hosts.

	<arg type='string' name='host' repeat='1'>
	One or more named hosts.
	</arg>
	
	<param type='string' name='interface' optional='0'>
	Name of the interface.
	</param>

	<param type='string' name='mac' optional='0'>
	MAC address of the interface.
	</param>
	
	<example cmd='set host interface interface backend-0-0 00:0e:0c:a7:5d:ff eth1'>
	Sets the logical interface of MAC address 00:0e:0c:a7:5d:ff to be eth1 
	</example>

	<example cmd='set host interface interface backend-0-0 interface=eth1 mac=00:0e:0c:a7:5d:ff'>
	Same as above.
	</example>
	"""
	
	def run(self, params, args):

		(interface, mac) = self.fillParams([
			('interface', None, True),
			('mac',       None, True)
			])

		if not len(args):
			raise ArgRequired(self, 'host')

		interfaces = defaultdict(list)
		for iface in self.call('list.host.interface'):
			interfaces[iface['host']].append({'interface': iface['interface'], 'mac': iface['mac']})

		for host in self.getHostnames(args):
			for iface in interfaces[host]:
				if interface == iface['interface'] and mac != iface['mac']:
					raise CommandError(self, f'Interface "{interface}" already exists on host "{host}"')
				# update data structure info
				elif mac == iface['mac']:
					iface['interface'] = interface

			self.db.execute("""
				update networks,nodes set 
				networks.device=%s where
				nodes.name=%s and networks.node=nodes.id and
				networks.mac like %s
				""", (interface, host, mac))


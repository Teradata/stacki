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


class command(stack.commands.SwitchArgumentProcessor,
	stack.commands.list.command):
	pass
	

class Command(command):
	"""
	List Interface, Port, Interface, Vlan, and Network of any hosts-to-switch
	relationships being managed.

	<arg optional='1' type='string' name='switch' repeat='1'>
	Zero, one or more switch names. If no switch names are supplies, info about
	all the known switchs is listed.
	</arg>

	<example cmd='list switch host switch-0-0'>
	List hosts connected to switch-0-0.
	</example>

	<example cmd='list switch host'>
	List any hosts on all known switches.
	</example>
	"""
	def run(self, params, args):
		switches = self.getSwitchNames(args)
	    
		self.beginOutput()

		header = [ 'switch', 'port', 'host', 'mac', 'interface', 'vlan' ]

		for switch in switches:
			for row in self.db.select(""" s.port, s.interface
					from switchports s, nodes n
					where s.switch = n.id and n.name = '%s'
					order by s.port """ % switch):

				port, ifaceid = row

				o = self.db.select(""" n.name, net.mac, net.device, net.vlanid
						from nodes n, networks net
						where n.id = net.node and net.id = %s """ % ifaceid)
				if len(o) != 1:
					continue

				host, mac, interface, vlan = o[0]
				self.addOutput(switch, [ port, host, mac, interface, vlan ])

		self.endOutput(header = header, trimOwner=False)

# @copyright@
# Copyright (c) 2006 - 2019 Teradata
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
from stack.commands import SwitchArgProcessor

class command(SwitchArgProcessor, stack.commands.list.command):
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

		header = ['switch', 'port', 'host', 'mac', 'interface', 'vlan']

		for switch in switches:
			for row in self.db.select("""
				switchports.port, switchports.interface
				FROM switchports, nodes
				WHERE switchports.switch=nodes.id AND nodes.name=%s
				ORDER BY switchports.port
			""", (switch,)):
				port, iface_id = row

				rows = self.db.select("""
					nodes.name, networks.mac, networks.device, networks.vlanid
					FROM nodes, networks
					WHERE nodes.id=networks.node AND networks.id=%s
				""", (iface_id,))

				if len(rows) != 1:
					continue

				self.addOutput(switch, [port, *rows[0]])

		self.endOutput(header=header, trimOwner=False)

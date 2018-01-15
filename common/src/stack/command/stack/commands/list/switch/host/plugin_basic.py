# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'basic'

	def run(self, hosts):
		switch_info = dict.fromkeys(hosts)
		host_info = {}

		for row in self.db.select(
			"""
			n.name, ns.device, nw.name, s.port, sw.name, s.vlan 
			from switchports s, nodes n, nodes nw, networks ns, subnets sw
			where s.host = n.id
			and ns.id = s.interface
			and sw.id = s.subnet
			and s.switch = nw.id
			"""):
			if row[2] in switch_info:
				host_info[row[0]] = row[1:]
	
		return { 'keys' : [ 'host', 
				    'interface',
				    'switch',
				    'port',
				    'subnet',
				    'vlan',
				    ],
			'values': host_info }


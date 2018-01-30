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

	<example cmd='list host switch-0-0'>
	List hosts connected to switch-0-0.
	</example>

	<example cmd='list switch'>
	List any hosts on all known switches.
	</example>
	"""
	def run(self, params, args):
	    
		hosts = self.getSwitchNames(args)
	    
		header = []
		values = {}
			
		for (provides, result) in self.runPlugins(hosts):
			header.extend(result['keys'])
			for h, v in result['values'].items():
				values[h] = v

		self.beginOutput()
		for host in values:
			self.addOutput(host, values[host])
		self.endOutput(header=header, trimOwner=False)


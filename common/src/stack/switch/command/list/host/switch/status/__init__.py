# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import stack.util
from stack.exception import CommandError

class command(stack.commands.SwitchArgumentProcessor,
	      stack.commands.list.command,
	      stack.commands.HostArgumentProcessor):
	pass

class Command(command):
	"""
	List information about a switch's port(s) that a host(s) is connected to.

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no hosts names are supplies, info about
	all the known hosts is listed.
	</arg>

	<example cmd='list host switch status backend-0-0'>
	List switch status info for any switches connected to backend-0-0.
	</example>

	<example cmd='list host switch status'>
	List switch status info for all switches connected to all hosts.
	</example>
	"""
	def run(self, params, args):

		self.hosts = self.getHostnames(args)
		_switches = self.getSwitchNames()
		self.beginOutput()
		for switch in self.call('list.host.interface', _switches):

			switch_name = switch['host']
			model = self.getHostAttr(switch_name, 'model')
			self.runImplementation(model, [switch])

		self.endOutput(header=['host', 'mac', 'interface', 'vlan', 'switch', 'port', 'speed', 'state'])

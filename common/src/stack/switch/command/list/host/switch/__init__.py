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
	List information about a host's interfaces and which switch ports they are connected to.

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no hosts names are supplied, info about
	all the known hosts is listed.
	</arg>

	<example cmd='list host switch backend-0-0'>
	List switch/port to host/interface relationship (if any).
	</example>

	<example cmd='list host switch backend-0-0 status=y'>
	List switch/port to host/interface relationship (if any) and display the link speed
	and link state.
	</example>
	"""

	def getPortStatus(self, switch, host, interface):
		if switch not in self.switchstatus:
			self.switchstatus[switch] = self.call('list.switch.status',
				[ switch, 'output-format=json' ])

		for o in self.switchstatus[switch]:
			if o['host'] == host and o['interface'] == interface:
				return o['speed'], o['state']

		return None, None
			

	def run(self, params, args):
		self.hosts = self.getHostnames(args)
		
		(status, ) = self.fillParams([ ('status', 'n') ])
		status = self.str2bool(status)

		header = [ 'host', 'mac', 'interface', 'vlan', 'switch', 'port' ]
		if status:
			header.extend([ 'speed', 'state' ])
			self.switchstatus = {}

		self.beginOutput()

		for host in self.hosts:
			for o in self.call('list.switch.host'):
				if o['host'] == host:
					line = [ o['mac'], o['interface'], o['vlan'], o['switch'], o['port'] ]
					if status:
						linkspeed, linkstate = self.getPortStatus(
							o['switch'], host, o['interface'])
						line.extend([ linkspeed, linkstate ])

					self.addOutput(host, line)

		self.endOutput(header = header, trimOwner = False)


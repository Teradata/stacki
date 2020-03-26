# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.commands import HostArgProcessor, SwitchArgProcessor
from stack.exception import (
	ParamRequired, ParamUnique, ParamType, CommandError, ArgUnique, ArgRequired, ArgError
)

class Command(HostArgProcessor, SwitchArgProcessor, stack.commands.set.switch.host.command):
	"""
	In the switch to host relation that Stacki keeps in its database, this command
	changes the name of a host's interface that is associated with a specific port
	on a switch.

	<arg type='string' name='switch' repeat='0' optional='0'>
	One switch name.
	</arg>

	<param type='string' name='host' repeat='0' optional='0'>
	One host name.
	</param>

	<param type='string' name='interface' optional='0'>
	Name of the interface.
	</param>

	<param type='string' name='port' optional='0'>
	The port number on the switch.
	</param>

	<example cmd='set switch host interface ethernet-231-1 host=stacki-231-3 interface=eth0 port=12'>
	Associates "eth0" on host "stacki-231-3" with port "12" on switch "ethernet-231-1".
	</example>
	"""

	def run(self, params, args):
		switches = self.getSwitchNames(args)
		if not switches:
			raise ArgRequired(self, 'switch')
		elif len(switches) > 1:
			raise ArgUnique(self, 'switch')
		switch = switches[0]

		(host, interface, port) = self.fillParams([
			('host', None),
			('interface', None),
			('port', None)
		])

		hosts = self.getHostnames([host])
		if not hosts:
			raise ParamRequired(self, ('host'))
		elif len(hosts) > 1:
			raise ParamUnique(self, 'host')
		host = hosts[0]

		try:
			port = int(port)
		except:
			raise ParamType(self, 'port', 'integer')

		# Check if the host/port is defined for this switch
		for row in self.call('list.switch.host', [switch]):
			if row['host'] == host and row['port'] == port:
				break
		else:
			raise ArgError(self, 'host/port', f'"{host}/{port}" not found')

		# See if the interface exists for this host
		row = self.db.select("""
			networks.id FROM networks, nodes
			WHERE nodes.name=%s AND networks.device=%s AND networks.node=nodes.id
		""", (host, interface))

		if not row:
			raise CommandError(
				self, f'interface "{interface}" does not exist for host "{host}"'
			)

		self.db.execute("""
			UPDATE switchports SET interface=%s
			WHERE port=%s AND switch=(SELECT id FROM nodes WHERE name=%s)
		""", (row[0][0], port, switch))

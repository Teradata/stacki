# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ParamRequired, ParamType, CommandError, ArgUnique, ArgRequired, ArgError

class Command(stack.commands.SwitchArgumentProcessor,
		stack.commands.HostArgumentProcessor,
		stack.commands.set.switch.host.command):
	"""
	In the switch to host relation that Stacki keeps in its database, this command
	changes the port association on the switch that this host's interface maps to.

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
	Associates port "12" on switch "ethernet-231-1" with interface "eth0" for host "stacki-231-3".
	</example>
	"""
	
	def run(self, params, args):
		(host, interface, port) = self.fillParams([
			('host', None),
			('interface', None),
			('port', None)
			])

		switches = self.getSwitchNames(args)
		if len(switches) == 0:
			raise ArgRequired(self, 'switch')
		if len(switches) > 1:
			raise ArgUnique(self, 'switch')
		switch = switches[0]

		hosts = self.getHostnames([host])
		host = hosts[0]

		if not host:
			raise ParamRequired(self, ('host'))
		if not interface:
			raise ParamRequired(self, ('interface'))
		if not port:
			raise ParamRequired(self, ('port'))

		try:
			port = int(port)
		except:
			raise ParamType(self, 'port', 'integer')

		#
		# check if the host/port is defined for this switch
		#
		found = False
		for o in self.call('list.switch.host', [ switch ]):
			if o['host'] == host and o['interface'] == interface:
				found = True
		if not found:
			raise ArgError(self, 'host/interface', '"%s/%s" not found' % (host, interface))

		row = self.db.select("""net.id from networks net, nodes n
			where n.name='%s' and net.device='%s'
			and net.node = n.id""" % (host, interface)) 

		if not row:
			raise CommandError(self,
				'interface "%s" does not exist for host "%s"' % (interface, host))

		interfaceid, = row[0]

		self.db.execute("""update switchports set port=%s
			where interface=%s and switch=(select id from nodes where name='%s')
			""" % (port, interfaceid, switch))


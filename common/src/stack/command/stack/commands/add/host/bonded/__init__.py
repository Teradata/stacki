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

import stack.commands
from stack.exception import ArgRequired, ArgUnique, CommandError


class Command(stack.commands.add.host.command):
	"""
	Add a channel bonded interface for a host

	<arg type='string' name='host'>
	Host name of machine
	</arg>
	
	<param type='string' name='channel'>
	The channel name (e.g., "bond0").
	</param>

	<param type='string' name='interfaces'>
	The physical interfaces that will be bonded. The interfaces
	can be a comma-separated list (e.g., "eth0,eth1") or a space-separated
	list (e.g., "eth0 eth1").
	</param>

	<param type='string' name='ip'>
	The IP address to assign to the bonded interface.
	</param>

	<param type='string' name='network'>
	The network to be assigned to this interface. This is a named network
	(e.g., 'private') and must be listable by the command
	'rocks list network'.
	</param>

	<param type='string' name='name' optional='1'>
	The host name associated with the bonded interface. If name is not
	specified, then the interface get the internal host name
	(e.g., backend-0-0).
	</param>

	<param type='string' name='options' optional='1'>
	Bonding Options. These are applied to the bonding device
	as BONDING_OPTS in the ifcfg-bond* files.
	</param>

	<example cmd='add host bonded backend-0-0 channel=bond0
		interfaces=eth0,eth1 ip=10.1.255.254 network=private'>
	Adds a bonded interface named "bond0" to backend-0-0 by bonding
	the physical interfaces eth0 and eth1, it assigns the IP address
	10.1.255.254 to bond0 and it associates this interface to the private
	network.
	</example>
	"""

	def run(self, params, args):
		host = self.getSingleHost(args)

		(channel, ifaces, ip, network, name, opts) = self.fillParams([
			('channel', None, True),
			('interfaces', None, True),
			('ip', None, True),
			('network', None, True),
			('name', ),
			('options',) 
		])

		# if name is not supplied, then give it the host name
		if not name:
			name = host
		
		# check if the network exists
		if self.db.count('(ID) from subnets where name=%s', (network,)) == 0:
			raise CommandError(self, f'network "{network}" does not exist')

		# If there is a comma, assume comma seperated. Else, assume whitespace.
		if ',' in ifaces:
			interfaces = [i.strip() for i in ifaces.split(',')]
		else:
			interfaces = [i.strip() for i in ifaces.split()]
			
		# Check if the physical interfaces exist. Also check if one of them 
		# is a default interface. If it is, then the bond becomes the default
		# interface for the machine.
		default_if = False
		for interface in interfaces:
			rows = self.db.select("""
				net.main from networks net, nodes n where
				net.device = %s and n.name = %s	and net.node = n.id
			""", (interface, host))

			if len(rows) == 0:
				raise CommandError(self,
					f'interface "{interface}" does not exist for host "{host}"'
				)

			for row in rows:
				if row[0] == 1:
					default_if = True

		# add the bonded interface
		cmd_args = [
			host,
			'interface=%s' % channel,
			'ip=%s' % ip,
			'module=bonding',
			'name=%s' % name,
			'network=%s' % network
		]

		if default_if:
			cmd_args.append("default=True")
		
		self.command('add.host.interface', cmd_args)

		# Set the options for the interface
		if opts:
			self.command('set.host.interface.options', [
				host,
				'interface=%s' % channel,
				'options=bonding-opts="%s"' % opts
			])
		
		# clear out all networking info from the physical interfaces and
		# then associate the interfaces with the bonded channel
		for i in interfaces:
			self.command('set.host.interface.network',
				(host, 'interface=%s' % i, 'network=NULL'))
			self.command('set.host.interface.ip',
				(host, 'interface=%s' % i, 'ip=NULL'))
			self.command('set.host.interface.name',
				(host, 'interface=%s' % i, 'name=NULL'))
			self.command('set.host.interface.channel',
				(host, 'interface=%s' % i, 'channel=%s' % channel))

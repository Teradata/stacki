# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ParamRequired, CommandError, ArgRequired


class Command(stack.commands.add.host.command):
	"""
	Add a bridge interface to a given host.
	<arg name="host">
	Hostname
	</arg>
	<param name="name" type="string">
	Name for the bridge interface.
	</param>
	<param name="interface" type="string">
	Physical interface to be bridged
	</param>
	<param name="network" type="string">
	Name of the network on which the physical
	device to be bridged exists.
	</param>
	<example cmd="add host bridge backend-0-0 name=cloudbr0
	network=private interface=eth0">
	This command will create a bridge called "cloudbr0", and
	attach it to physical interface eth0 and place it on the
	private network.
	</example>
	"""
	def run(self, params, args):
		hosts = self.getHosts(args)
		
		(bridge, interface, network) = self.fillParams([
			('name', None, True),
			('interface', ''),
			('network', ''),
		])

		if not interface and not network:
			raise ParamRequired(self, ('interface', 'network'))

		for host in hosts:
			sql = """nt.ip, nt.name, s.name, nt.device, nt.main, nt.options
				from networks nt, nodes n, subnets s where 
				nt.node=n.id and nt.subnet=s.id and n.name=%s"""
			values = [host]
			
			if network:
				sql += ' and s.name=%s'
				values.append(network)
			
			if interface:
				sql += ' and nt.device=%s'
				values.append(interface)

			rows = self.db.select(sql, values)
			if len(rows) == 0:
				raise CommandError(self, 'Could not find ' +
				("interface %s configured on " % interface if interface else '') +
				("network %s on " % network if network else '') +
				"host %s" % host)
			else:
				(ip, netname, net, dev, default_if, opts) = rows[0]

			# Set ip and subnet to NULL for original device
			self.command('set.host.interface.ip',
				[host, 'interface=%s' % dev, 'ip=NULL'])
			self.command('set.host.interface.network',
				[host, 'interface=%s' % dev, 'network=NULL'])
			
			# Create new bridge interface
			a_h_i_args = [host, "interface=%s" % bridge, 'network=%s' % net,
				'name=%s' % netname]
			if ip:
				a_h_i_args.append('ip=%s' % ip)
			self.command('add.host.interface',
				a_h_i_args)
			self.command('set.host.interface.options',
				[host, 'interface=%s' % bridge, 'options=bridge'])
			
			# Set the original device to point to the bridge
			self.command('set.host.interface.channel',
				[host, 'interface=%s' % dev, 'channel=%s' % bridge])
			if default_if == 1:
				self.command('set.host.interface.default',
					[host, 'interface=%s' % bridge, 'default=True'])

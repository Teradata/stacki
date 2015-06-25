# @SI_Copyright@
# @SI_Copyright@

import stack.commands
from stack.exception import *

class Command(stack.commands.Command,
	stack.commands.HostArgumentProcessor):
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
		(bridge, interface, network) = self.fillParams([
			('name', None, True),
			('interface',''),
			('network',''),
			])

		hosts = self.getHostnames(args)

		if not interface and not network:
                        raise ParamRequired(self, ('interface', 'network'))

		for host in hosts:
			sql = 'select nt.ip, nt.name, s.name, nt.device, nt.options ' +\
				'from networks nt, nodes n, subnets s where '+\
				'nt.node=n.id and nt.subnet=s.id and '      +\
				'n.name="%s"' % host
			
			if network:
				sql = sql + ' and s.name="%s"' % network
			if interface:
				sql = sql + ' and nt.device="%s"' % interface

			r = self.db.execute(sql)
			if r == 0:
				raise CommandError(self, 'Could not find ' +\
				("interface %s configured on " % interface if interface else '')+\
				("network %s on " % network if network else '')+\
				"host %s" % host)
			else:
				(ip, netname, net, dev, opts) = self.db.fetchone()

			if opts:
				opts = opts + ' bridgename=%s' % bridge
			else:
				opts = 'bridgename=%s' % bridge

			# Set ip and subnet to NULL for original device
			self.command('set.host.interface.ip',
				[host, 'interface=%s' % dev,'ip=NULL'])
			self.command('set.host.interface.subnet',
				[host, 'interface=%s' % dev, 'subnet=NULL'])
                        
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
			self.command('set.host.interface.options',
				[host, 'interface=%s' % dev, 'options=%s' % opts])

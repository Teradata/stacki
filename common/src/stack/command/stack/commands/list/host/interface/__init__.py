# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@

import stack.commands
import re


class Command(stack.commands.list.host.command):
	"""
	Lists the interface definitions for hosts. For each host supplied on
	the command line, this command prints the hostname and interface
	definitions for that host.

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, info about
	all the known hosts is listed.
	</arg>

	<example cmd='list host interface compute-0-0'>
	List network interface info for compute-0-0.
	</example>

	<example cmd='list host interface'>
	List network interface info for all known hosts.
	</example>
	"""

	def run(self, params, args):

		expanded, = self.fillParams([ ('expanded', 'false') ])
		expanded = self.str2bool(expanded)

		networks = {}
		if expanded:
			for row in self.call('list.network'):
				networks[row['network']] = row
			
		reg = re.compile('vlan.*')

		self.beginOutput()

		data = {}
		for host in self.getHostnames():
			data[host] = []
		for row in self.db.select("""
			distinctrow
			n.name,
			IF(net.subnet, sub.name, NULL),
			net.device, net.mac, net.main, net.ip,
			net.module, net.name, net.vlanid, net.options,
			net.channel
			from
			nodes n, networks net, subnets sub
			where
			net.node=n.id
			and (net.subnet=sub.id or net.subnet is NULL)
			order by net.device
			"""):
			data[row[0]].append(row[1:])
			
		for host in self.getHostnames(args):

			for (network,
			     interface,
			     mac,
			     default,
			     ip,
			     module,
			     name,
			     vlan,
			     options,
			     channel) in data[host]:

				if interface and reg.match(interface):
					# If device name matches vlan*
					# Then clear fields for printing
					mac = ip = module = name = None

				if not default:
					# Change False to None for easier
					# to read output.
					default = None
				else:
					default = True

				if not expanded:
					self.addOutput(host, (
						interface,
						default,
						network,
						mac,
						ip,
						name,
						module,
						vlan,
						options,
						channel
					))
				else:
					if network:
						mask    = networks[network]['mask']
						gateway = networks[network]['gateway']
						zone    = networks[network]['zone']
						dns     = networks[network]['dns']
						pxe     = networks[network]['pxe']
					else:
						mask    = None
						gateway = None
						zone    = None
						dns     = None
						pxe     = None
				
					self.addOutput(host, (
						interface,
						default,
						network,
						mac,
						ip,
						mask,
						gateway,
						name,
						zone,
						dns,
						pxe,
						module,
						vlan,
						options,
						channel
					))

		if not expanded:
			self.endOutput(header=[ 'host',
						'interface',
						'default',
						'network',
						'mac',
						'ip',
						'name',
						'module',
						'vlan',
						'options',
						'channel'
					])
		else:
			self.endOutput(header=[ 'host',
						'interface',
						'default',
						'network',
						'mac',
						'ip',
						'mask',
						'gateway',
						'name',
						'zone',
						'dns',
						'pxe',
						'module',
						'vlan',
						'options',
						'channel'
					])


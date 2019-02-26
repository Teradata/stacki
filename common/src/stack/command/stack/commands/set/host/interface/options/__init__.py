# @copyright@
# Copyright (c) 2006 - 2019 Teradata
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
from stack.exception import ParamRequired


class Command(stack.commands.set.host.interface.command):
	"""
	Sets the options for a device module for a named interface. On Linux,
	this will get translated to an entry in /etc/modprobe.conf.

	<arg type='string' name='host' repeat='1' optional='0'>
	One or more hosts.
	</arg>

	<param type='string' name='interface'>
	Name of the interface.
	</param>

	<param type='string' name='mac'>
	MAC address of the interface.
	</param>

	<param type='string' name='network'>
	Network name of the interface.
	</param>

	<param type='string' name='options' optional='0'>
	The options for an interface. Use options=NULL to clear.
	options="dhcp", and options="noreport" have
	special meaning. options="bonding-opts=\\"\\"" sets up bonding
	options for bonded interfaces
	</param>

	<example cmd='set host interface options backend-0-0 interface=eth1 options="Speed=10"'>
	Sets the option "Speed=10" for eth1 on e1000 on host backend-0-0.
	</example>

	<example cmd='set host interface options backend-0-0 interface=eth1 options=NULL'>
	Clear the options entry.
	</example>

	<example cmd='set host interface options backend-0-0 interface=eth0 options="dhcp"'>
	Linux only: Configure eth0 interface for DHCP instead of static.
	</example>

	<example cmd='set host interface options backend-0-0 interface=eth0 options="noreport"'>
	Linux only:  Tell stack report host interface to ignore this interface
	when writing configuration files
	</example>
	"""

	def run(self, params, args):
		hosts = self.getHosts(args)

		(options, interface, mac, network) = self.fillParams([
			('options', None, True),
			('interface', None),
			('mac', None),
			('network', None)
		])

		# Gotta have one of these
		if not any([interface, mac, network]):
			raise ParamRequired(self, ('interface', 'mac', 'network'))

		# Make sure interface, mac, and/or network exist on our hosts
		self.validate(hosts, interface, mac, network)

		# Options set to the string "NULL" is a null in the DB
		if options.upper() == 'NULL':
			options = None

		for host in hosts:
			if network:
				sql = """
					update networks,nodes,subnets set networks.options=%s
					where nodes.name=%s and subnets.name=%s
					and networks.node=nodes.id and networks.subnet=subnets.id
				"""
				values = [options, host, network]
			else:
				sql = """
					update networks,nodes set networks.options=%s
					where nodes.name=%s and networks.node=nodes.id
				"""
				values = [options, host]

			if interface:
				sql += " and networks.device=%s"
				values.append(interface)

			if mac:
				sql += " and networks.mac=%s"
				values.append(mac)

			self.db.execute(sql, values)

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

import string
import stack.commands
from stack.exception import ParamRequired


class Command(stack.commands.set.host.command):
	"""
	Sets the options for a device module for a named interface. On Linux,
	this will get translated to an entry in /etc/modprobe.conf.

	<arg type='string' name='host' repeat='1' optional='1'>
	One or more hosts.
	</arg>
	
	<param type='string' name='interface'>
	Name of the interface.
	</param>

	<param type='string' name='mac'>
	MAC address of the interface.
	</param>

	<param type='string' name='options'>
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

		(options, interface, mac) = self.fillParams([
			('options',    None, True),
			('interface', None),
			('mac',       None)
			])

		if not interface and not mac:
			raise ParamRequired(self, ('interface', 'mac'))
		
		if string.upper(options) == 'NULL':
			options = 'NULL'

		for host in self.getHostnames(args):
			if interface:
				self.db.execute("""
					update networks, nodes set 
					networks.options=NULLIF('%s','NULL') where
					nodes.name='%s' and networks.node=nodes.id and
					networks.device like '%s'
					""" % (options, host, interface))
			else:
				self.db.execute("""
					update networks, nodes set 
					networks.options=NULLIF('%s','NULL') where
					nodes.name='%s' and networks.node=nodes.id and
					networks.mac like '%s'
					""" % (options, host, mac))
		


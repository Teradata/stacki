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


import ipaddress
import stack.commands
from stack.exception import ArgUnique, CommandError


class Command(stack.commands.add.command):
	"""
	Add a network to the database. By default,
	the "private" network is already defined.

	<arg name='name'>
	Name of the new network.
	</arg>
	
	<param name='address' optional='0'>
	Network address.
	</param>
	
	<param name='mask' optional='0'>
	Network mask.
	</param>

	<param name='gateway'>
	Default gateway for the network. This is optional, not all networks
	require gateways.
	</param>
	
	<param name='mtu'>
	The MTU for the new network. Default is 1500.
	</param>

	<param name='zone'>
	The Domain name or the DNS Zone name to use
	for all hosts of this particular subnet. Default
	is set to the name of the network.
	</param>
	
	<param type='boolean' name='dns'>
	If set to True this network will be included in the builtin DNS server.
	The default value is false.
	</param>

	<param type='boolean' name='pxe'>
	If set to True this network will be managed by the builtin DHCP/PXE
	server.
	The default is False.
	</param>
	"""

	def run(self, params, args):

		if len(args) != 1:
			raise ArgUnique(self, 'network')
		name = args[0]

		if ' ' in name:
			raise CommandError(self, 'network name must not contain a space')

		(address, mask, gateway,
			 mtu, zone, dns, pxe) = self.fillParams([
				 ('address',	None, True),
				 ('mask',	None, True),
				 ('gateway',	None),
				 ('mtu',       '1500'),
				 ('zone',	name),
				 ('dns',	'n'),
				 ('pxe',	'n')
				 ])

		dns = self.str2bool(dns)
		pxe = self.str2bool(pxe)

		# Insert the name of the new network into the subnets
		# table if it does not already exist
			
		rows = self.db.select("""
			* from subnets where name='%s'
			""" % name)
		if len(rows):
			raise CommandError(self, 'network "%s" exists' % name)

		try:
			if ipaddress.IPv4Network(u"%s/%s" % (address, mask)):
				pass
		except:
			msg = '%s/%s is not a valid network address and subnet mask combination'
			raise CommandError(self, msg % (address, mask))

		self.db.execute("""
			insert into subnets 
			(name, address, mask, gateway, mtu, zone, dns, pxe)
			values 
			('%s', '%s', '%s', '%s', '%s', '%s', %s, %s)
			""" % (name, address, mask, gateway, mtu, zone, dns, pxe))

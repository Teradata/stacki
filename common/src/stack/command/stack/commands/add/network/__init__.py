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


import ipaddress
import stack.commands
from stack.exception import ArgUnique, CommandError, ArgRequired, ParamType


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
	The MTU for the new network. Default is unset.
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
		if len(args) == 0:
			raise ArgRequired(self, 'network')
		
		if len(args) != 1:
			raise ArgUnique(self, 'network')
		
		name = args[0]

		if ' ' in name:
			raise CommandError(self, 'network name must not contain a space')

		(address, mask, gateway, mtu, zone, dns, pxe) = self.fillParams([
			('address', None, True),
			('mask', None, True),
			('gateway', None),
			('mtu', None),
			('zone', name),
			('dns', 'n'),
			('pxe', 'n')
		])

		dns = self.str2bool(dns)
		pxe = self.str2bool(pxe)

		# A None gateway is a blank string
		if gateway is None:
			gateway = ''
		
		# The mtu parameter needs to be an int
		if mtu:
			try:
				mtu = int(mtu)
			except:
				raise ParamType(self, 'mtu', 'integer')
		
		# Make sure the network doesn't already exist
		if self.db.count('(ID) from subnets where name=%s', (name,)) != 0:
			raise CommandError(self, 'network "%s" exists' % name)

		# Check that we are a valid network
		try:
			if ipaddress.IPv4Network(u"%s/%s" % (address, mask)):
				pass
		except:
			msg = '%s/%s is not a valid network address and subnet mask combination'
			raise CommandError(self, msg % (address, mask))

		# Insert our data
		self.db.execute("""
			insert into subnets (name, address, mask, gateway, mtu, zone, dns, pxe)
			values (%s, %s, %s, %s, %s, %s, %s, %s)
		""", (name, address, mask, gateway, mtu, zone, dns, pxe))

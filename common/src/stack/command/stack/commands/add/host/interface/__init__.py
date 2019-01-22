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
from stack.exception import ParamRequired, ParamType, ArgUnique, CommandError
from stack.util import blank_str_to_None


class Command(stack.commands.add.host.command):
	"""
	Adds an interface to a host and sets the associated values.

	<arg type='string' name='host'>
	Host name of machine
	</arg>
	
	<param type='string' name='interface'>
	The interface name on the host (e.g., 'eth0', 'eth1')
	</param>

	<param type='string' name='ip'>
	The IP address to assign to the interface (e.g., '192.168.1.254')
	</param>

	<param type='string' name='network'>
	The name of the network to assign to the interface (e.g., 'private')
	</param>
	
	<param type='string' name='name'>
	The name to assign to the interface
	</param>
	
	<param type='string' name='mac'>
	The MAC address of the interface (e.g., '00:11:22:33:44:55')
	</param>
	
	<param type='string' name='module'>
	The device driver name (or module) of the interface (e.g., 'e1000')
	</param>

	<param type='string' name='vlan'>
	The VLAN ID to assign the interface
	</param>

	<param type='boolean' name='default'>
	If true, the name associated with this interface becomes the hostname
	and the interface's gateway becomes the default gateway.
	</param>

	<param type='string' name='channel'>
	The channel for an interface.
	</param>

	<example cmd='add host interface backend-0-0 interface=eth1 ip=192.168.1.2 network=private name=fast-0-0'>
	Add interface "eth1" to host "backend-0-0" with the given
	IP address, network assignment, and name.
	</example>
	"""

	def run(self, params, args):
		host = self.getSingleHost(args)

		(interface, mac, network, ip, module, 
		 name, vlan, default, options, channel, unsafe) = self.fillParams([
			('interface', None),
			('mac',       None),
			('network',   None),
			('ip',	      None),
			('module',    None),
			('name',      None),
			('vlan',      None),
			('default',   None),
			('options',   None),
			('channel',   None),
			('unsafe',    False)
		])

		# Make sure empty strings are converted to None
		(interface, mac, network, ip, module, 
		name, vlan, default, options, channel) = map(blank_str_to_None, (
			interface, mac, network, ip, module, 
		 	name, vlan, default, options, channel
		))
		
		# Gotta have an interface or mac
		if not interface and not mac:
			raise ParamRequired(self, ('interface', 'mac'))
		
		# Name can't be a FQDN (IE: have dots)
		if name and '.' in name:
			raise ParamType(self, 'name', 'non-FQDN (base hostname)')

		# Check if the network exists
		subnet_id = None
		if network:
			rows = self.db.select('ID from subnets where name = %s', (network,))
			if len(rows) == 0:
				raise CommandError(self, f'network "{network}" does not exist')
			else:
				subnet_id = rows[0][0]

		# The vlan parameter needs to be an int
		if vlan:
			try:
				vlan = int(vlan)
			except:
				raise ParamType(self, 'vlan', 'integer')
		
		# Stacki can use the usafe parameter to disable the check if the
		# interface already exists.  The spreadsheet loading uses this
		# since before add.host.interface is called all the interfaces
		# are removed.
		
		unsafe = self.str2bool(unsafe)
		if not unsafe:
			for row in self.call('list.host.interface', [ host ]):
				if interface == row['interface']:
					raise CommandError(self, f'interface {interface} exists on {host}')
				if mac and mac == row['mac']:
					raise CommandError(self, f'mac {mac} exists on {host}')

		# Some parameters accept the string 'NULL' to mean put a NULL in the db
		if ip and ip.upper() == 'NULL':
			ip = None
		
		if module and module.upper() == 'NULL':
			module = None
		
		if channel and channel.upper() == 'NULL':
			channel = None
		
		# If name is set to 'NULL' it gets the host name, but confusingly
		# if name is None it gets a NULL in the db. Not sure the history
		# of this unique behavior.
		if name and name.upper() == 'NULL':
			name = host
		
		# If vlan is 0 then it should be NULL in the db
		if vlan == 0:
			vlan = None
		
		# Default is a boolean
		default = self.str2bool(default)

		# If ip is set to "auto" we let the 'set' command handle it
		ip_is_auto = False
		if ip and ip.upper() == "AUTO":
			ip_is_auto = True
			ip = None

			# The auto ip feature requires a network parameter
			if subnet_id is None:
				raise ParamRequired(self, 'network')

		# Unset other default interface if the added one is the default interface
		if default:
			self.db.execute("""
				update networks set main=0
				where node=(select id from nodes where name=%s)
				""", (host,)
				)


		# Insert all our data
		self.db.execute("""
			insert into networks(
				node, mac, ip, name, device, subnet, 
				module, vlanid, options, channel, main
			)
			values (
				(select id from nodes where name=%s),
				%s, %s, %s, %s, %s, %s, %s, %s, %s, %s
			)
		""",(
			host, mac, ip, name, interface, subnet_id,
			module,	vlan, options, channel, default
		))

		# Handle auto ip if needed
		if ip_is_auto:
			self.command('set.host.interface.ip', (
				host,
				f'mac={mac}' if mac else f'interface={interface}',
				'ip=auto'
			))

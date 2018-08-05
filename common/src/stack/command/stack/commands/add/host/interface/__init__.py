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

		hosts = self.getHostnames(args)
		(interface, mac, network, ip, module, 
		 name, vlan, default, options, channel, unsafe) = self.fillParams([
			 ('interface', None),
			 ('mac',       None),
			 ('network',   None),
			 ('ip',	       None),
			 ('module',    None),
			 ('name',      None),
			 ('vlan',      None),
			 ('default',   None),
			 ('options',   None),
			 ('channel',   None),
			 ('unsafe',    False)
			 ])

		
		if not interface and not mac:
			raise ParamRequired(self, ('interface', 'mac'))
		if name and len(name.split('.')) > 1:
			raise ParamType(self, 'name', 'non-FQDN (base hostname)')
		if len(hosts) != 1:
			raise ArgUnique(self, 'host')

		host = hosts[0]

		# Stacki can use the usafe parameter to disable the check if the
		# interface already exists.  The spreadsheet loading uses this
		# since before add.host.interface is called all the interfaces
		# are removed.
		
		unsafe = self.str2bool(unsafe)
		if not unsafe:
			for dict in self.call('list.host.interface', [ host ]):
				if interface == dict['interface']:
					raise CommandError(self, 'interface exists')
				if mac and mac == dict['mac']:
					raise CommandError(self, 'mac exists')


		fields = [ 'network', 'ip', 'module', 'name', 'vlan', 'default', 'options', 'channel' ]

		# Insert the mac or interface into the database and then use
		# that to key off of for all the subsequent fields.
		# Give the MAC preferrence (need to pick one) but still do the
		# right thing when MAC and Interface are both specified.
		#
		# The MAC handle includes some optimization to include more
		# information on the initial insert, in order to reduce the
		# updates for each extra field.
		
		if mac:
			handle = 'mac=%s' % mac
			fields.append('interface')

			keys = [ 'node', 'mac' ]
			vals = [
				'(select id from nodes where name="%s")' % host,
				'"%s"' % mac
				]

			if interface:
				fields.remove('interface')
				keys.append('device')
				vals.append('"%s"' % interface)
			if network:
				fields.remove('network')
				keys.append('subnet')
				vals.append('(select id from subnets s where s.name="%s")' % network)
			if ip and ip != 'auto':
				fields.remove('ip')
				keys.append('ip')
				vals.append('NULLIF("%s","NULL")' % ip.upper())
			if name:
				if name.upper() == "NULL":
					name = host
				fields.remove('name')
				keys.append('name')
				vals.append('"%s"' % name)
			if default:
				fields.remove('default')
				keys.append('main')
				vals.append('%d' % self.str2bool(default))
			if options:
				fields.remove('options')
				keys.append('options')
				vals.append('"%s"' % options)
			
			self.db.execute("""
				insert into networks(%s) values (%s)
				""" % (','.join(keys), ','.join(vals)))

			
		else:
			handle = 'interface=%s' % interface
			fields.append('mac')
			
			self.db.execute("""
				insert into networks(node, device)
				values ((select id from nodes where name='%s'), '%s')
				""" % (host, interface)) 

		for key in fields:
			if key in params:	
				self.command('set.host.interface.%s' % key,
					(host, handle, "%s=%s" % (key, params[key])))


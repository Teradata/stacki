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
from stack.exception import ArgUnique


class Command(stack.commands.config.host.command):
	"""
	!!! STACKIQ INTERNAL COMMAND ONLY !!!

	Configures host interfaces in the database.
	This command should only be called from a post section in a kickstart
	file.

	<arg type='string' name='host'>
	Host name of machine
	</arg>

	<param type='string' name='interface'>
	Interface names (e.g., "eth0"). If multiple interfaces are supplied,
	then they must be comma-separated.
	</param>

	<param type='string' name='mac'>
	MAC addresses for the interfaces. If multiple MACs are supplied,
	then they must be comma-separated.
	</param>

	<param type='string' name='module'>
	Driver modules to be loaded for the interfaces. If multiple modules
	are supplied, then they must be comma-separated.
	</param>

	<param type='string' name='flag'>
	Flags for the interfaces. If flags for multiple interfaces
	are supplied, then they must be comma-separated.
	</param>
	"""

	def run(self, params, args):
		(interface, mac, module, flag) = self.fillParams([
			('interface', None),
			('mac', None),
			('module', None),
			('flag', None) ])

		hosts = self.getHostnames(args)

		if len(hosts) != 1:
			raise ArgUnique(self, 'host')

		host = hosts[0]

		sync_config = 0

		discovered_macs = []

		if mac:
			macs = mac.split(',')
		else:
			macs = []

		if interface:
			interfaces = interface.split(',')
		else:
			interfaces = []

		if module:
			modules = module.split(',')
		else:
			modules = []
		if flag:
			flags = flag.split(',')
		else:
			flags = []

		for i in range(0, len(macs)):
			a = (macs[i], )

			if len(interfaces) > i:
				a += (interfaces[i], )
			else:
				a += ('', )

			if len(modules) > i:
				a += (modules[i], )
			else:
				a += ('', )
			
			if len(flags) > i:
				a += (flags[i], )
			else:
				a += ('', )
			
			discovered_macs.append(a)

		pre_config = self.command('list.host.interface', [host])
		#
		# First, assign the correct names to the mac addresses
		#
		for (mac, interface, module, ks) in discovered_macs:
			rows = self.db.select("""mac from networks
				where mac = %s """,mac)
			if rows:
				self.command('set.host.interface.interface',
					[host, 'interface=%s' % interface, 'mac=%s' % mac])
			else:
				continue

			if module:
				self.command('set.host.interface.module',
					[host, 'interface=%s' % interface, 'module=%s' % module])

		#
		# Add any missing/new interfaces to the database
		#
		for (mac, interface, module, ks) in discovered_macs:
			rows = self.db.select("""mac from networks
				where mac = %s """, mac)
			if not rows:
				# Check if the interface exists without a MAC.
				r = self.db.select("""device from networks, nodes
					where device = %s and networks.node = nodes.id
					and nodes.name=%s""", (interface, host))
				if not r:
					# If it does not, add the interface before setting MAC addresses
					self.command('add.host.interface',
						[host, 'interface=%s' % interface])
				# Update the MAC address of the interface
				self.command('set.host.interface.mac', [host, 'interface=%s' % interface, 'mac=%s' % mac ])
			# Update the kernel module if that information is sent back
			if module:
				self.command('set.host.interface.module',
					[host, 'interface=%s' % interface, 'module=%s' % module])


		post_config = self.command('list.host.interface', [host])

		if pre_config != post_config:
			self.command('sync.config')

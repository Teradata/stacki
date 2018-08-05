# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import CommandError
from stack.switch.x1052 import SwitchDellX1052

#
# IMPORTANT!!!
#
# this is NOT a configuration file -- it is a list of instructions the switch
# should execute. so you'll see "setting the port into default mode", then you'll
# see the actual port configuration. this is because commands sent to the switch
# are "additive", for example, if a port is set to accept VLAN 8 and then later
# you tell it to accept VLAN 13, it will now be configured to accept *both*
# VLAN 8 and 13. if you just want it to accept VLAN 13, you need to first put
# the port in its default state (no VLANs), then add the VLAN you want.
#
# we must do this because there are no "remove" or "delete" commands for this 
# switch.
#

class Implementation(stack.commands.Implementation):
	def clearPort(self):
		self.owner.addOutput('localhost', ' switchport mode general')
		self.owner.addOutput('localhost', ' switchport general allowed vlan remove 2-4094')


	def doPort(self, switch, host, port):
		self.owner.addOutput('localhost', '!')
		self.owner.addOutput('localhost', 'interface gigabitethernet1/0/%s' % port)

		attr = self.owner.getHostAttr(host, 'appliance')
		if attr == 'frontend':
			#
			# special case for the frontend -- we need to make this
			# a 'trunk' port which allows all VLAN traffic to pass,
			# that is, the frontend needs to concurrently talk to
			# hosts in *all* VLANs.
			#
			self.owner.addOutput('localhost', ' switchport mode trunk')
			return

		#
		# first put the port into the default state. this clears
		# all previous port config
		#
		self.clearPort()

		#
		# configure the port
		#
		native = False

		for s in self.owner.call('list.switch.host', [ switch ]):
			if s['host'] == host and s['port'] == port:
				if not s['vlan']:
					continue

				vlan = s['vlan']

				if s['interface'] == 'ipmi':
					self.owner.addOutput('localhost',
						' switchport general allowed vlan add %s tagged' % vlan)
				else:
					#
					# the "native" vlan
					#
					self.owner.addOutput('localhost',
						' switchport general allowed vlan add %s untagged' % vlan)
					self.owner.addOutput('localhost',
						' switchport general pvid %s' % vlan)

					native = True

		if not native:
			#
			# there is no "native untagged" configuration for this port, so let's
			# enable the default VLAN (e.g., VLAN 1).
			#
			self.owner.addOutput('localhost',
				' switchport general allowed vlan add 1 untagged')
			self.owner.addOutput('localhost',
				' switchport general pvid 1')


	def run(self, args):
		switch = args[0]

		switch_name = switch['switch']
		switch_interface, *xargs = self.owner.call('list.host.interface', [switch_name])
		switch_network, *xargs = self.owner.call('list.network', [switch_interface['network']])
		# Start of configuration file
		self.owner.addOutput('localhost',
			'<stack:file stack:name="/tftpboot/pxelinux/%s/new_config">' % switch_name)

		# Write the static ip block
		self.owner.addOutput('localhost', '!')
		self.owner.addOutput('localhost', 'interface vlan 1')
		self.owner.addOutput('localhost',
			' ip address %s %s' % (switch_interface['ip'], switch_network['mask']))
		self.owner.addOutput('localhost',' no ip address dhcp')
		self.owner.addOutput('localhost', '!')

		#
		# find all the VLAN ids
		#
		vlans = []
		for o in self.owner.call('list.host.interface', [ 'a:backend' ]):
			if o['vlan']:
				vlan = str(o['vlan'])
				if vlan not in vlans:
					vlans.append(vlan)

		self.owner.addOutput('localhost', 'vlan %s' % ','.join(vlans))

		#
		# turn off global spanning tree
		#
		self.owner.addOutput('localhost', 'no spanning-tree')

		#
		# create a list of host/port 
		#
		hostport = []
		for s in self.owner.call('list.switch.host', [ switch_name ]):
			host = s['host']
			port = s['port']

			hp = (host, port)
			if hp not in hostport:
				self.doPort(switch_name, host, port)
				hostport.append(hp)

		self.owner.addOutput('localhost', '!')
		self.owner.addOutput('localhost', '</stack:file>')


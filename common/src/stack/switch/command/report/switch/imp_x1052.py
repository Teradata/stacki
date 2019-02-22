# @copyright@
# Copyright (c) 2006 - 2019 Teradata
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
		self.owner.addOutput('localhost', 'interface gi1/0/%s' % port)

		#
		# find out if we need to set the port as a 'trunk' port. a trunk port 
		# allows all VLAN traffic to pass.
		#
		istrunk = False

		if self.owner.getHostAttr(host, 'switch_port_mode') == 'trunk':
			istrunk = True
		else:
			#
			# if more that one host is mapped to this port, then it must
			# be configured as a trunk port
			#
			x = 0
			for s in self.owner.call('list.switch.host', [ switch ]):
				if s['port'] == port:
					x = x + 1
					if x > 1:
						istrunk = True
						break

		if istrunk:
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
		self.owner.addOutput('localhost', '!')

		#
		# turn off global spanning tree
		#
		self.owner.addOutput('localhost', 'no spanning-tree')

		#
		# user-defined global configuration (e.g., SNMP)
		#
		attr = self.owner.getHostAttr(switch_name, 'switch_global_config')
		if attr:
			self.owner.addOutput('localhost', attr)

		if self.owner.nukeswitch:
			#
			# put the switch in a default state:
			#
			#	- remove all vlan info
			#	- set all ports to the default vlan of 1
			#
			self.owner.addOutput('localhost', 'no vlan 2-4094')
			self.owner.addOutput('localhost', '!')
			self.owner.addOutput('localhost', 'interface range gi1/0/1-48')
			self.owner.addOutput('localhost', ' switchport mode general') 
			self.owner.addOutput('localhost',
				' switchport general allowed vlan add 1 untagged')
			self.owner.addOutput('localhost', '!')
			self.owner.addOutput('localhost', 'interface range te1/0/1-4')
			self.owner.addOutput('localhost', ' switchport mode general') 
			self.owner.addOutput('localhost',
				' switchport general allowed vlan add 1 untagged')
		else:
			#
			# find all the VLAN ids for all non-frontend components
			#
			vlans = []

			for o in self.owner.call('list.host'):
				if o['appliance'] == 'frontend':
					continue

				for p in self.owner.call('list.host.interface', [ o['host'] ]):
					if p['vlan']:
						vlan = str(p['vlan'])
						if vlan not in vlans:
							vlans.append(vlan)

			if len(vlans):
				self.owner.addOutput('localhost', 'vlan %s' % ','.join(vlans))

			configured = []
			for s in self.owner.call('list.switch.host', [ switch_name ]):
				host = s['host']
				port = s['port']

				if port not in configured:
					self.doPort(switch_name, host, port)
					configured.append(port)

		self.owner.addOutput('localhost', '!')
		self.owner.addOutput('localhost', '</stack:file>')


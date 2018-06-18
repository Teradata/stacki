# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import CommandError
from stack.switch import SwitchDellX1052


class Implementation(stack.commands.Implementation):
	def run(self, args):

		switch = args[0]
		switch_name = switch['switch']
		switch_interface, *xargs = self.owner.call('list.host.interface', [switch_name])
		switch_network, *xargs = self.owner.call('list.network', [switch_interface['network']])
		# Get the frontend since it requires a different
		# config block
		frontend = self.owner.db.getHostname('localhost')

		hosts = self.owner.db.select("""
		n.name, s.port, i.vlanid
		from switchports s, nodes n, nodes sw, subnets sub, networks i
		where i.node = n.id
		and s.switch = sw.id
		and i.subnet = sub.id
		and s.interface = i.id
		and s.switch = (select id from nodes where name='%s')
		""" % switch_name)

		# Start of configuration file
		self.owner.addOutput(frontend, '<stack:file stack:name="/tftpboot/pxelinux/%s_upload">' % switch_name)

		# Write the static ip block
		self.owner.addOutput(frontend, '!')
		self.owner.addOutput(frontend, 'interface vlan 1')
		self.owner.addOutput(frontend,'  ip address %s %s' % (switch_interface['ip'], switch_network['mask']))
		self.owner.addOutput(frontend,'  no ip address dhcp')
		self.owner.addOutput(frontend, '!')


		#
		# calculate the highest VLAN value
		#
		max_vlan = None
		for o in self.owner.call('list.host.interface', [ 'a:backend' ]):
			if o['network'] != switch_interface['network']:
				continue

			try:
				x = int(o['vlan'])
				if not max_vlan or x > max_vlan:
					max_vlan = x
			except:
				pass

		if max_vlan:
			# Set blank vlan from 2-max_vlan
			#
			# The reason we are creating blank vlan ids is so we 
			# don't accidentally try to assign a nonexistent vlanid
			#
			self.owner.addOutput(frontend, 'vlan 2-%s' % max_vlan)

		for (host, port, vlan) in hosts:
			attr = self.owner.getHostAttr(host, 'appliance')

			# if vlan isn't set, set vlan to '1'
			if not vlan:
				vlan = '1'

			# if frontend, write difference block
			if attr == 'frontend':
				self.owner.addOutput(frontend, '!')
				self.owner.addOutput(frontend, 'interface gigabitethernet1/0/%s' % port)
				self.owner.addOutput(frontend,'  switchport mode general')
				self.owner.addOutput(frontend,'  switchport general allowed vlan add 2-%s tagged' % max_vlan)
				self.owner.addOutput(frontend,'  switchport general allowed vlan add 1 untagged')
			else:
				self.owner.addOutput(frontend, '!')
				self.owner.addOutput(frontend, 'interface gigabitethernet1/0/%s' % port)
				self.owner.addOutput(frontend, ' switchport access vlan %s' % vlan)

		self.owner.addOutput(frontend, '!')
		self.owner.addOutput(frontend, '</stack:file>')

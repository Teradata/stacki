#
# @SI_COPYRIGHT@
# @SI_COPYRIGHT@
#

import os
import sys
import re
import shlex
import stack.commands

class Implementation(stack.commands.Implementation):
	def run(self, args):
		
		host = args[0]
		
		rows = self.owner.call('list.host.interface', [host, 'expanded=True'])

		udev_output = ""

		for row in rows:

			mac = row['mac']
			ip  = row['ip']
			device = row['interface']
			netname = row['name']
			netmask = row['mask']
			subnet = row['network']
			module = row['module']
			options = row['options']
			channel = row['channel']
			gateway = row['gateway']
			vlanid  = row['vlan']

			mtu = None
			if subnet:
				subnetInfo = self.owner.call('list.network',[subnet])
				mtu = subnetInfo[0]['mtu']

			# Host attributes can override the subnets tables
			# definition of the netmask.

			x = self.owner.getHostAttr(host, 'network.%s.netmask' % netname)
			if x:
				netmask = x
			
			optionlist = []
			if options:
				optionlist = shlex.split(options)
			if 'noreport' in optionlist:
				continue # don't do anything if noreport set

			if device == 'ipmi':
				self.owner.addOutput(host, '<stack:file stack:name="/etc/sysconfig/ipmi" stack:perms="500">')
				self.owner.writeIPMI(host, ip, channel,
					netmask, gateway, vlanid)
				self.owner.addOutput(host, '</stack:file>')

				# ipmi is special, skip the standard stuff
				continue

			if device and device[0:4] != 'vlan':
				#
				# output a script to update modprobe.conf
				#
				self.owner.writeModprobe(host, device, module,
					optionlist)

			if self.owner.interface:
				if self.owner.interface == device:
					self.owner.writeConfig(host, mac, ip, device,
						netmask, vlanid, mtu, optionlist,
						channel)
			else:
				s = '<stack:file stack:name="'
				s += '/etc/sysconfig/network-scripts/ifcfg-'
				s += '%s">' % (device)

				self.owner.addOutput(host, s)
				self.owner.writeConfig(host, mac, ip, device,
					netmask, vlanid, mtu, optionlist, channel)
				self.owner.addOutput(host, '</stack:file>')

				ib_re = re.compile('^ib[0-9]+$')
				if not ib_re.match(device):
					udev_output += 'SUBSYSTEM=="net", '
					udev_output += 'ACTION=="add", '
					udev_output += 'DRIVERS=="?*", '
					udev_output += 'ATTR{address}=="%s", ' % mac
					udev_output += 'ATTR{type}=="1", '
					udev_output += 'KERNEL=="eth*", '
					udev_output += 'NAME="%s"\n\n' % device

		if udev_output:
			self.owner.addOutput(host, '<stack:file stack:name="/etc/udev/rules.d/70-persistent-net.rules">')
			self.owner.addOutput(host, udev_output)
			self.owner.addOutput(host, '</stack:file>')


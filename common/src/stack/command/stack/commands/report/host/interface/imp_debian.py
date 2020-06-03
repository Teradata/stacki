# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import re
import shlex
import stack.commands
from stack.commands import Warn


class Implementation(stack.commands.Implementation):
	def run(self, args):
		
		host = args[0]

		if not self.owner.interface:
			# TODO - can we kill off the ability to call report
			# host interface with a specified interface, currently
			# when we do this we drop the SUX wrapping tags which
			# doesn't sound right. This is probably dead code and
			# can get cleaned up. That's why the above if exists,
			# still need to write the top level interfaces file.
			self.owner.addOutput(host, '<stack:file stack:name="/etc/network/interfaces">')
			self.owner.addOutput(host, 'source-directory /etc/network/interfaces.d')
			self.owner.addOutput(host, '')
			self.owner.addOutput(host, 'auto lo')
			self.owner.addOutput(host, 'iface lo inet loopback')
			self.owner.addOutput(host, '</stack:file>')

		udev_output = ""

		for row in self.owner.call('list.host.interface', [host, 'expanded=True']):
			mac = row['mac']
			ip  = row['ip']
			device = row['interface']
			netmask = row['mask']
			subnet = row['network']
			module = row['module']
			options = row['options']
			channel = row['channel']
			gateway = row['gateway']
			vlanid	= row['vlan']
			default = row['default']

			if ip and not subnet:
				Warn(f'WARNING: skipping interface "{device}" on host "{host}" - '
				      'interface has an IP but no network')
				continue

			# If we don't have a device, we don't need a config file
			if not device:
				continue

			mtu = None
			if subnet:
				subnetInfo = self.owner.call('list.network', [subnet])
				mtu = subnetInfo[0]['mtu']

			# Host attributes can override the subnets tables
			# definition of the netmask.

			x = self.owner.getHostAttr(host, 'network.%s.netmask' % subnet)
			if x:
				netmask = x
			
			optionlist = []
			if options:
				optionlist = shlex.split(options)
			if 'noreport' in optionlist:
				continue # don't do anything if noreport set

			if device == 'ipmi':
				# TODO - anyone with a debian box and a bmc?
				continue

			if device and device[0:4] != 'vlan':
				# TODO - writeModprobe(host, device, module, optionlist) for debian, is this needed?
				pass

			if self.owner.interface:
				if self.owner.interface == device:
					self.writeConfig(host, mac, ip, device, netmask, vlanid, mtu, optionlist, channel, default)
			else:
				self.owner.addOutput(host, f'<stack:file stack:name="/etc/network/interfaces.d/{device}">')
				self.owner.addOutput(host, '# AUTHENTIC STACKI')
				self.writeConfig(host, mac, ip, device, netmask, vlanid, mtu, optionlist, channel, default)
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

		if udev_output and False:
			# TODO - skipping for now, not need on the pi and don't know if the is correct for debian
			self.owner.addOutput(host, '<stack:file stack:name="/etc/udev/rules.d/70-persistent-net.rules">')
			self.owner.addOutput(host, udev_output)
			self.owner.addOutput(host, '</stack:file>')

			
	def writeConfig(self, host, mac, ip, device, netmask, vlanid, mtu, options, channel, default):


		if 'dhcp' in options:
			self.owner.addOutput(host, f'auto {device}')
			self.owner.addOutput(host, f'allow-hotplug {device}')
			self.owner.addOutput(host, f'iface {device} inet dhcp')
		else:
			self.owner.addOutput(host, f'auto {device}')
			self.owner.addOutput(host, f'iface {device} inet static')
			self.owner.addOutput(host, f'  address {ip}')
			self.owner.addOutput(host, f'  netmask {netmask}')

		# TODO - advanced stuff like ib, vlan, virtual, bonding,
		# bridges, all the freaky stuff

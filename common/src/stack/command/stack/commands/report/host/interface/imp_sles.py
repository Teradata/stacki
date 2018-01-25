# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import re
import shlex
import ipaddress
import stack.commands


class Implementation(stack.commands.Implementation):
	def run(self, args):

		host = args[0]

		result = self.owner.call('list.host.interface', [ host ])
		udev_output = ""
		for o in result:
			interface = None
			ip = None
			netmask = None
			netname = None
			network = None
			broadcast = None

			interface = o['interface']
			ip = o['ip']
			netname = o['network']
			vlanid = o['vlan']
			mac = o['mac']
			channel = o['channel']
			options = []
			if o['options']:
				options = shlex.split(o['options'])

			ib_re = re.compile('^ib[0-9]+$')
			if mac:
				if not ib_re.match(interface) and interface != 'ipmi':
					udev_output += 'SUBSYSTEM=="net", '
					udev_output += 'ACTION=="add", '
					udev_output += 'DRIVERS=="?*", '
					udev_output += 'ATTR{address}=="%s", ' % mac
					udev_output += 'ATTR{type}=="1", '
					udev_output += 'KERNEL=="eth*", '
					udev_output += 'NAME="%s"\n\n' % interface

			if not interface:
				continue

			if netname:
				netresult = self.owner.call('list.network', [ netname ])
				for net in netresult:
					if net['network'] == netname:
						network = net['address']
						netmask = net['mask']
						ipnet = ipaddress.IPv4Network('%s/%s' % (network, netmask))
						broadcast = '%s' % ipnet.broadcast_address
						gateway = net['gateway']
						if gateway == 'None':
							gateway = None
						break

			if interface == 'ipmi':
				ipmisetup = '/tmp/ipmisetup'
				self.owner.addOutput(host, '<stack:file stack:name="%s">' % ipmisetup)
				self.owner.writeIPMI(host, ip, channel, netmask, gateway, vlanid)
				self.owner.addOutput(host, '</stack:file>')
				self.owner.addOutput(host, 'chmod 500 %s' % ipmisetup)
				continue

			if len(interface.split(':')) == 2:
				#
				# virtual interface configuration
				#
				self.owner.addOutput(host, 
						     '<stack:file stack:mode="append" stack:name="/etc/sysconfig/network/ifcfg-%s">' 
						     % interface.split(':')[0])
				vnum = interface.split(':')[1]
				if ip:
					self.owner.addOutput(host, 'IPADDR%s=%s' % (vnum, ip.strip()))
				if netmask:
					self.owner.addOutput(host, 'NETMASK%s=%s' % (vnum, netmask.strip()))
				if network:
					self.owner.addOutput(host, 'NETWORK%s=%s' % (vnum, network.strip()))
				if broadcast:
					self.owner.addOutput(host, 'BROADCAST%s=%s' % (vnum, broadcast.strip()))
					
				self.owner.addOutput(host, 'LABEL%s=%s' % (vnum, vnum))

			else:
				self.owner.addOutput(host, 
						     '<stack:file stack:name="/etc/sysconfig/network/ifcfg-%s">' 
						     % interface)
				if vlanid and self.owner.host_based_routing(host):
					parent_device = interface.strip().split('.')[0]
					self.owner.addOutput(host, 'ETHERDEVICE=%s' % parent_device)
					self.owner.addOutput(host, 'VLAN=yes')
				else:
					self.owner.addOutput(host, 'USERCONTROL=no')

				dhcp = 'dhcp' in options
				if dhcp:
					self.owner.addOutput(host, 'BOOTPROTO=dhcp')

				if 'onboot=no' in options:
					self.owner.addOutput(host, 'STARTMODE=manual')
				else:
					if ip or dhcp or channel or 'bridge' in options:
						#
						# if there is an IP address, or this
						# interface should DHCP, or anything in
						# the 'channel' field (e.g., this is a
						# bridged interface), or if 'bridge' is in
						# the options, then turn this interface on
						#
						self.owner.addOutput(host, 'STARTMODE=auto')
					else:
						self.owner.addOutput(host, 'STARTMODE=off')
				
				if ip:
					self.owner.addOutput(host, 'IPADDR=%s' % ip.strip())
				if netmask:
					self.owner.addOutput(host, 'NETMASK=%s' % netmask.strip())
				if network:
					self.owner.addOutput(host, 'NETWORK=%s' % network.strip())
				if broadcast:
					self.owner.addOutput(host, 'BROADCAST=%s' % broadcast.strip())

				if mac:
					self.owner.addOutput(host, 'HWADDR=%s' % mac.strip())

				#
				# if this is a bridged interface, then go look for the
				# physical interface this bridge is associated with
				#
				if 'bridge' in options:
					for p in result:
						if p['channel'] == interface:
							self.owner.addOutput(host, 'BRIDGE=yes')
							self.owner.addOutput(host, 'BRIDGE_FORWARDDELAY=0')
							self.owner.addOutput(host, 'BRIDGE_STP=off')
							self.owner.addOutput(host, 'BRIDGE_PORTS=%s' % p['interface'])
							break

			self.owner.addOutput(host, '\n')
			self.owner.addOutput(host, '</stack:file>')

		if udev_output:
			self.owner.addOutput(host, 
					     '<stack:file stack:name="/etc/udev/rules.d/70-persistent-net.rules">')
			self.owner.addOutput(host, udev_output)
			self.owner.addOutput(host, '</stack:file>')


RollName = "stacki"

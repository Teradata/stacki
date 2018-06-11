# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import re
import shlex
import ipaddress
from stack.bool import str2bool
import stack.commands


class Implementation(stack.commands.Implementation):
	def run(self, args):

		host = args[0]

		bond_reg = re.compile('bond[0-9]+')
		udev_output = ""

		result = self.owner.call('list.host.interface', [ 'expanded=true', host ])
		for o in result:
			interface = o['interface']
			default   = str2bool(o['default'])
			ip        = o['ip']
			netname   = o['network']
			vlanid    = o['vlan']
			mac       = o['mac']
			if mac:
				mac = mac.lower()
			channel   = o['channel']
			options   = o['options']
			netmask   = o['mask']
			gateway   = o['gateway']

			startmode = 'off'
			bootproto = 'static'

			if netname and ip and netmask:
				net       = ipaddress.IPv4Network('%s/%s' % (ip, netmask), strict=False)
				broadcast = str(net.broadcast_address)
				network   = str(net.network_address)
			else:
				broadcast = None
				network   = None

			if options:
				options = shlex.split(o['options'])
			else:
				options = []

			if 'noreport' in options:
				continue # don't do anything if noreport set

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
					self.owner.addOutput(host, 'IPADDR%s=%s' % (vnum, ip))
				if netmask:
					self.owner.addOutput(host, 'NETMASK%s=%s' % (vnum, netmask))
				if network:
					self.owner.addOutput(host, 'NETWORK%s=%s' % (vnum, network))
				if broadcast:
					self.owner.addOutput(host, 'BROADCAST%s=%s' % (vnum, broadcast))
					
				self.owner.addOutput(host, 'LABEL%s=%s' % (vnum, vnum))

			else:
				self.owner.addOutput(host, 
				     '<stack:file stack:name="/etc/sysconfig/network/ifcfg-%s">' 
				     % interface)

				if vlanid and self.owner.host_based_routing(host, interface, vlanid):
					parent_device = interface.strip().split('.')[0]
					self.owner.addOutput(host, 'ETHERDEVICE=%s' % parent_device)
					self.owner.addOutput(host, 'VLAN=yes')
				else:
					self.owner.addOutput(host, 'USERCONTROL=no')

				dhcp = 'dhcp' in options

				if dhcp:
					bootproto = 'dhcp'
					if default:
						self.owner.addOutput(host, 'DHCLIENT_SET_HOSTNAME="yes"')
						self.owner.addOutput(host, 'DHCLIENT_SET_DEFAULT_ROUTE="yes"')
					else:
						self.owner.addOutput(host, 'DHCLIENT_SET_HOSTNAME="no"')
						self.owner.addOutput(host, 'DHCLIENT_SET_DEFAULT_ROUTE="no"')

				if 'onboot=no' in options:
					startmode = 'manual'
				else:
					if ip or dhcp or channel or 'bridge' in options:
						#
						# if there is an IP address, or this
						# interface should DHCP, or anything in
						# the 'channel' field (e.g., this is a
						# bridged or bonded interface), or if 'bridge'
						# is in the options, then turn this interface on
						#
						startmode = 'auto'
					else:
						startmode = 'off'
				
				if not dhcp:
					if ip:
						self.owner.addOutput(host, 'IPADDR=%s' % ip)
					if netmask:
						self.owner.addOutput(host, 'NETMASK=%s' % netmask)
					if network:
						self.owner.addOutput(host, 'NETWORK=%s' % network)
					if broadcast:
						self.owner.addOutput(host, 'BROADCAST=%s' % broadcast)

				if mac:
					self.owner.addOutput(host, 'HWADDR=%s' % mac.strip())

				#
				# bonded interface, e.g., 'bond0'
				#
				if bond_reg.match(interface):
					#
					# if a 'bond*' device is present, then always make
					# sure it is enabled on boot.
					#
					startmode = 'auto'

					self.owner.addOutput(host, 'BONDING_MASTER=yes')

					#
					# find the interfaces that are part of this bond
					#
					i = 0
					for p in result:
						if p['channel'] == interface:
							self.owner.addOutput(host,
								'BONDING_SLAVE%d="%s"'
								% (i, p['interface']))
							i = i + 1

					#
					# Check if there are bonding options set
					#
					for opt in options:
						if opt.startswith('bonding-opts='):
							i = opt.find('=')
							bo = opt[i + 1:]
							self.owner.addOutput(host,
								'BONDING_MODULE_OPTS="%s"' % bo)
							break

				#
				# check if this is part of a bonded channel
				#
				if channel and bond_reg.match(channel):
					startmode = 'auto'
					bootproto = 'none'

				self.owner.addOutput(host, 'STARTMODE=%s' % startmode)
				self.owner.addOutput(host, 'BOOTPROTO=%s' % bootproto)

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

# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import re
import shlex
import stack.commands
from stack.exception import CommandError


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
			vlanid	= row['vlan']
			default = row['default']

			if ip and not netname:
				raise CommandError(self, f'interface "{interface}" on host "{row["host"]}" has an IP but no network')

			mtu = None
			if subnet:
				subnetInfo = self.owner.call('list.network', [subnet])
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
				self.writeModprobe(host, device, module,
					optionlist)

			if self.owner.interface:
				if self.owner.interface == device:
					self.writeConfig(host, mac, ip, device,
						netmask, vlanid, mtu, optionlist,
						channel, default)
			else:
				s = '<stack:file stack:name="'
				s += '/etc/sysconfig/network-scripts/ifcfg-'
				s += '%s">' % (device)

				self.owner.addOutput(host, s)
				self.writeConfig(host, mac, ip, device,
					netmask, vlanid, mtu, optionlist, channel, default)
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

	def writeConfig(self, host, mac, ip, device, netmask, vlanid, mtu,
			options, channel, default):

		configured = 0

		# Should we set up DHCP on this device?
		if 'dhcp' in options:
			dhcp = 1 # tell device to dhcp, explicitly
		else:
			dhcp = 0


		self.owner.addOutput(host, 'DEVICE=%s' % device)

		if mac:
			# Check for IB
			ib_re = re.compile('^ib[0-9]+$')
			if not ib_re.match(device):
				self.owner.addOutput(host, 'MACADDR=%s' % mac)

		if dhcp:
			self.owner.addOutput(host, 'BOOTPROTO=dhcp')
			configured = 1
			if default:
				self.owner.addOutput(host, 'DEFROUTE=yes')
		else:
			if ip and netmask:
				self.owner.addOutput(host, 'IPADDR=%s' % ip)
				self.owner.addOutput(host, 'NETMASK=%s' % netmask)
				self.owner.addOutput(host, 'BOOTPROTO=static')
				configured = 1

		#
		# If device is a bonding device
		#
		bond_reg = re.compile('bond[0-9]+')
		if bond_reg.match(device):
			#
			# if a 'bond*' device is present, then always make
			# sure it is enabled on boot.
			#
			if not configured:
				self.owner.addOutput(host, 'BOOTPROTO=none')
				configured = 1
			
			#
			# Check if there are bonding options set
			#
			for opt in options:
				if opt.startswith('bonding-opts='):
					i = opt.find('=')
					bo = opt[i + 1:]
					self.owner.addOutput(host, 'BONDING_OPTS="%s"' % bo)
					break
		#
		# check if this is part of a bonded channel
		#
		if channel and bond_reg.match(channel):
			self.owner.addOutput(host, 'BOOTPROTO=none')
			self.owner.addOutput(host, 'MASTER=%s' % channel)
			self.owner.addOutput(host, 'SLAVE=yes')
			configured = 1

		# If device is a bridge device
		if 'bridge' in options:
			self.owner.addOutput(host, 'TYPE=Bridge')

			#
			# if there is no IP address associated with this
			# bridge, still make sure it enabled on boot.
			#
			if not configured:
				self.owner.addOutput(host, 'BOOTPROTO=none')

			#
			# Don't write the MTU in the bridge configuration
			# file. The MTU will be specified in the underlying
			# ifcfg-eth* file
			#
			mtu = None
			configured = 1

		# If device is part of a bridge

		if channel:
			sql = """select net.options from
				networks net, nodes n, subnets s where
				net.device='%s' and n.name='%s' and
				net.node=n.id""" % (channel, host)
			rows = self.db.execute(sql)
			if rows:
				options = self.db.fetchone()
				if "bridge" in options:
					self.owner.addOutput(host, 'BOOTPROTO=none')
					self.owner.addOutput(host, 'BRIDGE=%s' % channel)
					configured = 1

		if vlanid:
			self.owner.addOutput(host, 'VLAN=yes')
			configured = 1

		if not configured:
			self.owner.addOutput(host, 'BOOTPROTO=none')
			self.owner.addOutput(host, 'ONBOOT=no')
		else:
			if 'onboot=no' in options:
				self.owner.addOutput(host, 'ONBOOT=no')
			else:
				self.owner.addOutput(host, 'ONBOOT=yes')

		if mtu:
			self.owner.addOutput(host, 'MTU=%s' % mtu)
		
	def writeModprobe(self, host, device, module, options):
		if not module:
			return

		self.owner.addOutput(host, '<![CDATA[')
		self.owner.addOutput(host, 'grep -v "\<%s\>" /etc/modprobe.conf > /tmp/modprobe.conf' % (device))

		self.owner.addOutput(host,
			"echo 'alias %s %s' >> /tmp/modprobe.conf" %
			(device, module))

		modopts = None
		# Check if module options are present
		for opt in options:
			if opt.startswith('mod-opts='):
				i = opt.find('=')
				modopts = opt[i + 1:]
				break
		if modopts:
			self.owner.addOutput(host,
				"echo 'options %s %s' >> /tmp/modprobe.conf" %
				(module, options))

		self.owner.addOutput(host, 'mv /tmp/modprobe.conf /etc/modprobe.conf')
		self.owner.addOutput(host, 'chmod 444 /etc/modprobe.conf')
		self.owner.addOutput(host, ']]>')


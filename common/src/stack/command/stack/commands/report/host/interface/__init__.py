# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
# 
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@

import re
import stack.commands


class Command(stack.commands.HostArgumentProcessor,
	stack.commands.report.command):
	"""
	Output the network configuration file for a host's interface.

	<arg type='string' name='host'>
	One host name.
	</arg>

	<param type='string' name='interface'>
	Output a configuration file for this host's interface (e.g. 'eth0').
	If no 'interface' parameter is supplied, then configuration files
	for every interface defined for the host will be output (and each
	file will be delineated by &lt;file&gt; and &lt;/file&gt; tags).
	</param>

	<example cmd='report host interface compute-0-0 interface=eth0'>
	Output a network configuration file for compute-0-0's eth0 interface.
	</example>
	"""

	def writeConfig(self, host, mac, ip, device, netmask, vlanid, mtu,
			options, channel):

		configured = 0

		# Should we set up DHCP on this device?
		if 'dhcp' in options:
			dhcp = 1 # tell device to dhcp, explicitly
		else:
			dhcp = 0


		self.addOutput(host, 'DEVICE=%s' % device)

		if mac:
			# Check for IB
			ib_re = re.compile('^ib[0-9]+$')
			if not ib_re.match(device):
				self.addOutput(host, 'MACADDR=%s' % mac)

		if dhcp:
			self.addOutput(host, 'BOOTPROTO=dhcp')
			configured = 1
		else:
			if ip and netmask:
				self.addOutput(host, 'IPADDR=%s' % ip)
				self.addOutput(host, 'NETMASK=%s' % netmask)
				self.addOutput(host, 'BOOTPROTO=static')
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
				self.addOutput(host, 'BOOTPROTO=none')
				configured = 1
			
			#
			# Check if there are bonding options set
			#
			for opt in options:
				if opt.startswith('bonding-opts='):
					i = opt.find('=')
					bo = opt[i + 1:]
					self.addOutput(host, 'BONDING_OPTS="%s"' % bo)
					break
		#
		# check if this is part of a bonded channel
		#
		if channel and bond_reg.match(channel):
			self.addOutput(host, 'BOOTPROTO=none')
			self.addOutput(host, 'MASTER=%s' % channel)
			self.addOutput(host, 'SLAVE=yes')
			configured = 1

		# If device is a bridge device
		if 'bridge' in options:
			self.addOutput(host, 'TYPE=Bridge')

			#
			# if there is no IP address associated with this
			# bridge, still make sure it enabled on boot.
			#
			if not configured:
				self.addOutput(host, 'BOOTPROTO=none')

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
					self.addOutput(host, 'BOOTPROTO=none')
					self.addOutput(host, 'BRIDGE=%s' % channel)
					configured = 1

		if vlanid:
			self.addOutput(host, 'VLAN=yes')
			configured = 1

		if not configured:
			self.addOutput(host, 'BOOTPROTO=none')
			self.addOutput(host, 'ONBOOT=no')
		else:
			if 'onboot=no' in options:
				self.addOutput(host, 'ONBOOT=no')
			else:
				self.addOutput(host, 'ONBOOT=yes')

		if mtu:
			self.addOutput(host, 'MTU=%s' % mtu)
		

	def writeModprobe(self, host, device, module, options):
		if not module:
			return

		self.addOutput(host, '<![CDATA[')
		self.addOutput(host, 'grep -v "\<%s\>" /etc/modprobe.conf > /tmp/modprobe.conf' % (device))

		self.addOutput(host,
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
			self.addOutput(host,
				"echo 'options %s %s' >> /tmp/modprobe.conf" %
				(module, options))

		self.addOutput(host, 'mv /tmp/modprobe.conf /etc/modprobe.conf')
		self.addOutput(host, 'chmod 444 /etc/modprobe.conf')
		self.addOutput(host, ']]>')


	def writeIPMI(self, host, ip, channel, netmask, gateway, vlan=0):
		defaults = [ ('IPMI_SI', 'yes'),
			('DEV_IPMI', 'yes'),
			('IPMI_WATCHDOG', 'no'),
			('IPMI_WATCHDOG_OPTIONS', '"timeout=60"'),
			('IPMI_POWEROFF', 'no'),
			('IPMI_POWERCYCLE', 'no'),
			('IPMI_IMB', 'no') ]

		for var, default in defaults:
			attr = self.getHostAttr(host, var)
			if not attr:
				attr = default
			self.addOutput(host, '%s=%s' % (var, attr))

		self.addOutput(host, 'ipmitool lan set %s ipsrc static'
			% (channel))
		self.addOutput(host, 'ipmitool lan set %s ipaddr %s'
			% (channel, ip))
		self.addOutput(host, 'ipmitool lan set %s netmask %s'
			% (channel, netmask))

		if not gateway:
			gateway = '0.0.0.0'
		self.addOutput(host, 'ipmitool lan set %s defgw ipaddr %s'
			% (channel, gateway))

		self.addOutput(host, 'ipmitool lan set %s arp respond on'
			% (channel))

		if vlan:
			vlanid = vlan
		else:
			vlanid = "off"
		self.addOutput(host, "ipmitool lan set %s vlan id %s" % (channel, vlanid))

		self.addOutput(host, 'ipmitool lan set %s access on'
			% (channel))
		self.addOutput(host, 'ipmitool lan set %s user'
			% (channel))
		self.addOutput(host, 'ipmitool lan set %s auth ADMIN PASSWORD'
			% (channel))

		# add a root user at id 2
		self.addOutput(host, 'ipmitool user set name 2 root')

		password = self.getHostAttr(host, 'ipmi_password')
		if not password:
			password = 'admin'

		self.addOutput(host, 'ipmitool user set password 2 %s'
			% (password))
		self.addOutput(host, 'ipmitool channel setaccess ' +
			'%s ' % (channel) +
			'2 link=on ipmi=on callin=on privilege=4')


	def run(self, params, args):

		self.interface, = self.fillParams([('interface', ), ])
		self.beginOutput()


		hosts = self.getHostnames(args)
		for host in hosts:
			osname = self.getHostAttr(host, 'os')
			self.runImplementation(osname, [host])

		self.endOutput(padChar='', trimOwner=True)


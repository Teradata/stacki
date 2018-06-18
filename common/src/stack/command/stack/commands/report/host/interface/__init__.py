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

import re
import stack.commands


class Command(stack.commands.HostArgumentProcessor,
	stack.commands.SwitchArgumentProcessor,
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

	<example cmd='report host interface backend-0-0 interface=eth0'>
	Output a network configuration file for backend-0-0's eth0 interface.
	</example>
	"""



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
		self.addOutput(host, 'ipmitool user enable 2')
		self.addOutput(host, 'ipmitool channel setaccess ' +
			'%s ' % (channel) +
			'2 link=on ipmi=on callin=on privilege=4')


	def host_based_routing(self, host, interface, vlan):
		"""Checks to see if host should be using host based routing or 
		switch based routing.
		"""
		# Use host based routing always on the frontend
		# Might change in the future but the default is True
		if self.db.getHostAppliance(host) == 'frontend':
			return True

		# Use switch-based VLAN tagging if there is an entry in the switchports table
		# that matches this host/interface/vlan
		for o in self.call('list.host.switch', [ host ]):
			if o['interface'] == interface and o['vlan'] == vlan:
				return False

		return True

	def run(self, params, args):

		self.interface, = self.fillParams([('interface', ), ])
		self.beginOutput()


		hosts = self.getHostnames(args)
		for host in hosts:
			osname = self.getHostAttr(host, 'os')
			self.runImplementation(osname, [host])

		self.endOutput(padChar='', trimOwner=True)


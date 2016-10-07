# @SI_Copyright@
#                               stacki.com
#                                  v3.3
# 
#      Copyright (c) 2006 - 2016 StackIQ Inc. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
# 
# 	 "This product includes software developed by StackIQ" 
#  
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY STACKIQ AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL STACKIQ OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@
# 
# @Copyright@
#  				Rocks(r)
#  		         www.rocksclusters.org
#  		         version 5.4 (Maverick)
#  
# Copyright (c) 2000 - 2010 The Regents of the University of California.
# All rights reserved.	
#  
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
#  
# 	"This product includes software developed by the Rocks(r)
# 	Cluster Group at the San Diego Supercomputer Center at the
# 	University of California, San Diego and its contributors."
# 
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.  The name of the
# software includes the following terms, and any derivatives thereof:
# "Rocks", "Rocks Clusters", and "Avalanche Installer".  For licensing of 
# the associated name, interested parties should contact Technology 
# Transfer & Intellectual Property Services, University of California, 
# San Diego, 9500 Gilman Drive, Mail Code 0910, La Jolla, CA 92093-0910, 
# Ph: (858) 534-5815, FAX: (858) 534-7345, E-MAIL:invent@ucsd.edu
#  
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @Copyright@

import re
import shlex
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

	def isPhysicalHost(self, host):
		#
		# determine if this is 'physical' machine, that is, not a VM.
		#
		rows = self.db.execute("""show tables like 'vm_nodes' """)

		if rows == 0:
			#
			# the Xen roll is not installed, so all hosts are
			# physical hosts
			#
			retval = 1
		else:
			rows = self.db.execute("""select vn.id from
				vm_nodes vn, nodes n where
				n.name = '%s' and vn.node = n.id""" % (host))

			if rows == 0:
				#
				# this host is *not* in the VM nodes table, so
				# it is a physical host
				#
				retval = 1
			else:
				retval = 0

		return retval


	def writeIPMI(self, host, ip, channel, netmask, gateway):
		defaults = [ ('IPMI_SI', 'yes'),
			('DEV_IPMI', 'yes'),
			('IPMI_WATCHDOG', 'no'),
			('IPMI_WATCHDOG_OPTIONS', '"timeout=60"'),
			('IPMI_POWEROFF', 'no'),
			('IPMI_POWERCYCLE', 'no'),
			('IPMI_IMB', 'no') ]

		self.addOutput(host,
			'<file name="/etc/sysconfig/ipmi" perms="500">')

		for var, default in defaults:
			attr = self.db.getHostAttr(host, var)
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

		attr = self.db.getHostAttr(host, 'ipmi_password')
		if attr:
			password = attr
		else:
			password = 'admin'

		self.addOutput(host, 'ipmitool user set password 1 %s'
			% (password))

		self.addOutput(host, 'ipmitool lan set %s access on'
			% (channel))
		self.addOutput(host, 'ipmitool lan set %s user'
			% (channel))
		self.addOutput(host, 'ipmitool lan set %s auth ADMIN PASSWORD'
			% (channel))

		# add a root user at id 2
		self.addOutput(host, 'ipmitool user set name 2 root')
		self.addOutput(host, 'ipmitool user set password 2 %s'
			% (password))
		self.addOutput(host, 'ipmitool channel setaccess ' +
			'%s ' % (channel) +
			'2 link=on ipmi=on callin=on privilege=4')

		self.addOutput(host, '</file>')


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
				self.addOutput(host, 'HWADDR=%s' % mac)

		if dhcp:
			self.addOutput(host, 'BOOTPROTO=dhcp')
			self.addOutput(host, 'ONBOOT=yes')
			configured = 1
		else:
			if ip and netmask:
				self.addOutput(host, 'IPADDR=%s' % ip)
				self.addOutput(host, 'NETMASK=%s' % netmask)
				self.addOutput(host, 'BOOTPROTO=static')
				self.addOutput(host, 'ONBOOT=yes')
				configured = 1

		# If device is a bonding device
		bond_reg = re.compile('bond[0-9]+')
		if bond_reg.match(device):
			# Check if there are bonding options set
			for opt in options:
				if opt.startswith('bonding-opts='):
					i = opt.find('=')
					bo = opt[i+1:]
					self.addOutput(host,
						'BONDING_OPTS="%s"' \
						% bo)
					break
		#
		# check if this is part of a bonded channel
		#
		if channel and bond_reg.match(channel):
			self.addOutput(host, 'BOOTPROTO=none')
			self.addOutput(host, 'ONBOOT=yes')
			self.addOutput(host, 'MASTER=%s' % channel)
			self.addOutput(host, 'SLAVE=yes')
			configured = 1

		# If device is a bridge device
		if 'bridge' in options:
			self.addOutput(host, 'TYPE=Bridge')

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
					self.addOutput(host, 'ONBOOT=yes')
					self.addOutput(host, 'BRIDGE=%s' % channel)
					configured = 1

		if vlanid:
			self.addOutput(host, 'VLAN=yes')
			self.addOutput(host, 'ONBOOT=yes')
			configured = 1

		if not configured:
			self.addOutput(host, 'BOOTPROTO=none')
			self.addOutput(host, 'ONBOOT=no')

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
				modopts = opt[i+1:]
				break
		if modopts:
			self.addOutput(host,
				"echo 'options %s %s' >> /tmp/modprobe.conf" %
				(module, options))

		self.addOutput(host, 'mv /tmp/modprobe.conf /etc/modprobe.conf')
		self.addOutput(host, 'chmod 444 /etc/modprobe.conf')
		self.addOutput(host, ']]>')


	def run(self, params, args):

		self.interface, = self.fillParams([('interface', ), ])
		self.beginOutput()

                for host in self.getHostnames(args):
			osname = self.db.getHostAttr(host, 'os')
			f = getattr(self, 'run_%s' % (osname))
			f(host)

		self.endOutput(padChar = '')

	def run_ubuntu(self, host):
		pass

	def run_sles(self, host):
		import os

		result = self.call('list.host.interface', [ host ])
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

			if not netname or not ip or not interface:
				continue

			netresult = self.call('list.network', [ netname ])
			for net in netresult:
				if net['network'] == netname:
					network = net['address']
					netmask = net['mask']
					broadcast = os.popen("/usr/bin/ipcalc -b %s %s" % (ip, netmask) + " | awk -F =  '{print $2}'").read()
					break

			if not network or not netmask or not broadcast:
				continue

			print("cat > /etc/sysconfig/network/ifcfg-%s << '__EOF__'" % (interface))
			print('IPADDR=%s' % ip.strip())
			print('NETMASK=%s' % netmask.strip())
			print('NETWORK=%s' % network.strip())
			print('BROADCAST=%s' % broadcast.strip())
			print('STARTMODE=auto')
			print('USERCONTROL=no')
			print('__EOF__')
                
	def run_redhat(self, host):
		self.db.execute("""select id, name, mask, mtu
			from subnets""")

		#
		# need to prefetch the subnets data because we can't do a
		# self.db.execute() in the middle of a self.db.fetchall() loop
		# because it resets the MySQL cursor
		#
		subnets = {}
		for row in self.db.fetchall():
			id = row[0]
			subnets[id] = row

		self.db.execute("""select distinctrow 
			net.mac, net.ip, net.device, net.vlanid,
			net.subnet, net.module, net.options, net.channel,
			s.gateway from networks net, nodes n, subnets s
			where net.node = n.id and net.subnet = s.id 
			and n.name = "%s" order by net.device""" % (host))

		udev_output = ""

		for row in self.db.fetchall():
			(mac, ip, device, vlanid, subnetid, module, options,
				channel, gateway) = row

			netname = None
			netmask = None
			mtu = None

			if subnetid:
				id, netname, netmask, mtu = subnets[subnetid]

			# Host attributes can override the subnets tables
			# definition of the netmask.

			x = self.db.getHostAttr(host,
				'network.%s.netmask' % netname)
			if x:
				netmask = x
			
			optionlist = []
			if options:
				optionlist = shlex.split(options)
			if 'noreport' in optionlist:
				continue # don't do anything if noreport set

			if device == 'ipmi':
				self.writeIPMI(host, ip, channel, netmask,
					gateway)

				# ipmi is special, skip the standard stuff
				continue

			if device and device[0:4] != 'vlan':
				#
				# output a script to update modprobe.conf
				#
				self.writeModprobe(host, device, module,
					optionlist)

			if vlanid:
				#
				# look up the name of the interface that
				# maps to this VLAN spec
				#
				rows = self.db.execute("""select net.device from
					networks net, nodes n where
					n.id = net.node and n.name = '%s'
					and net.subnet = %d and
					net.device not like 'vlan%%' """ %
					(host, subnetid))

				if rows:
					dev, = self.db.fetchone()
					#
					# check if already referencing 
					# a physical device
					#
					if dev != device:
						device = '%s.%d' % (dev, vlanid)

			#
			# for interfaces that have bridges attached, make sure
			# we get the MTU of the network that is associated
			# with the *bridge* and 
			#
			for opt in optionlist:
				if opt.startswith('bridgename='):
					bridge = opt.split('=')[1]

					rows = self.db.execute("""select
						s.mtu from networks net,
						nodes n, subnets s where
						n.name = '%s' and
						n.id = net.node and 
						net.device = '%s' and
						net.subnet = s.id """ %
						(host, bridge))

					if rows:
						mtu, = self.db.fetchone()

			if self.interface:
				if self.interface == device:
					self.writeConfig(host, mac, ip, device,
						netmask, vlanid, mtu, optionlist,
						channel)
			else:
				s = '<file name="'
				s += '/etc/sysconfig/network-scripts/ifcfg-'
				s += '%s">' % (device)

				self.addOutput(host, s)
				self.writeConfig(host, mac, ip, device,
					netmask, vlanid, mtu, optionlist, channel)
				self.addOutput(host, '</file>')

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
			self.addOutput(host, '<file name="/etc/udev/rules.d/70-persistent-net.rules">')
			self.addOutput(host, udev_output)
			self.addOutput(host, '</file>')


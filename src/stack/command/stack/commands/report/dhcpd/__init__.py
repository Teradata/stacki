# @SI_Copyright@
#                               stacki.com
#                                  v4.0
# 
#      Copyright (c) 2006 - 2017 StackIQ Inc. All rights reserved.
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

import os
import os.path
import sys
import stack
import string

import ipaddress

import stack.commands
import stack.text

class Command(stack.commands.HostArgumentProcessor,
	stack.commands.report.command):
	"""
	Output the DHCP server configuration file.
	"""


	def writeDhcpDotConf(self):
		self.addOutput('', '<stack:file stack:name="/etc/dhcp/dhcpd.conf">')

		self.addOutput('', stack.text.DoNotEdit())
		self.addOutput('', 'ddns-update-style none;')

		# Build a dictionary of DHCPD server addresses
		# for each subnet that serves PXE (DHCP).

		servers = {}
		for row in self.db.select("""
			s.name, n.ip from
			nodes nd, subnets s, networks n where 
			s.id       = n.subnet and 
			s.pxe      = TRUE     and 
			n.node     = nd.id    and 
			nd.name    = '%s'
			""" % self.db.getHostname()):
			servers[row[0]]    = row[1]
			servers['default'] = row[1]
		if len(servers) > 2:
			del servers['default']

		for (netname, network, netmask, gateway, zone) in self.db.select("""
			name, address, mask, gateway, zone from 
			subnets where
			pxe = TRUE
			"""):

			self.addOutput('', '\nsubnet %s netmask %s {'
				% (network, netmask))

			self.addOutput('', '\tdefault-lease-time\t\t1200;')
			self.addOutput('', '\tmax-lease-time\t\t\t1200;')

			ipnetwork = ipaddress.IPv4Network(unicode(
				network + '/' + netmask))
			self.addOutput('', '\toption routers\t\t\t%s;' % gateway)
			self.addOutput('', '\toption subnet-mask\t\t%s;' % netmask)
			self.addOutput('', '\toption broadcast-address\t%s;' %
				ipnetwork.broadcast_address)
			self.addOutput('', '}\n')

		data = { }
		for row in self.db.select("name from nodes order by rack, rank"):
			data[row[0]] = []
			
		for row in self.db.select("""
			nodes.name, n.mac, n.ip, n.device
			from networks n, nodes where
			n.node     = nodes.id and
			n.mac is not NULL and
			(n.vlanid is NULL or n.vlanid = 0)
			"""):
			data[row[0]].append(row[1:])

		kickstartable = {}
		for name in data.keys():
			kickstartable[name] = False
		argv = data.keys()
		argv.append('attr=kickstartable')
		for row in self.call('list.host.attr', argv):
			kickstartable[row['host']] = self.str2bool(row['value'])

		for name in data.keys():

			mac = None
			ip  = None
			dev = None
			
			#
			# look for a physical private interface that has an
			# IP address assigned to it.
			#
			for (mac, ip, dev) in data[name]:
				if not ip:
					ip = self.resolve_ip(name, dev)
				netname = None
				if ip:
					r = self.db.select("""
					s.name from subnets s, networks nt,
					nodes n where nt.node=n.id and
					n.name='%s' and nt.subnet=s.id and
					nt.ip = '%s'""" % (name, ip))
					if r:
						(netname, ) = r[0]
				if ip and mac and dev and netname:
					self.addOutput('', '\nhost %s.%s.%s {' %
						(name, netname, dev))
					self.addOutput('', '\toption host-name\t"%s";' % name)

					self.addOutput('', '\thardware ethernet\t%s;' % mac)
					self.addOutput('', '\tfixed-address\t\t%s;' % ip)

					if kickstartable[name]:
						self.addOutput('', '\tfilename\t\t"pxelinux.0";')

						server = servers.get(netname)
						if not server:
							server = servers.get('default')

						self.addOutput('','\tserver-name\t\t"%s";'
							% server)
						self.addOutput('','\tnext-server\t\t%s;'
							% server)
				
					self.addOutput('', '}')

		self.addOutput('', '</stack:file>')

	def resolve_ip(self, host, device):
			(ip, channel), = self.db.select("""nt.ip,
			nt.channel from networks nt, nodes n
			where n.name='%s' and nt.device='%s' and
			nt.node=n.id""" % (host, device))
			if channel:
				return self.resolve_ip(host, channel)
			return ip


	def writeDhcpSysconfig(self):
		self.addOutput('', '<stack:file stack:name="/etc/sysconfig/dhcpd">')
		self.addOutput('', stack.text.DoNotEdit())

		devices = ''
		for device, in self.db.select("""
			device from
			networks n, subnets s
			where n.node = (select id from nodes where name = '%s') and
			s.pxe = TRUE and
			n.subnet = s.id and
			n.ip is not NULL and
			(n.vlanid is NULL or n.vlanid = 0)
			""" % self.db.getHostname()):
			devices += '%s ' % device

		self.addOutput('', 'DHCPDARGS="%s"' % devices.strip())
		self.addOutput('', '</stack:file>')
		



	def run(self, params, args):

		self.beginOutput()
		self.writeDhcpDotConf()
		self.writeDhcpSysconfig()
		self.endOutput(padChar='')


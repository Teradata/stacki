# @SI_Copyright@
#                             www.stacki.com
#                                  v1.0
# 
#      Copyright (c) 2006 - 2015 StackIQ Inc. All rights reserved.
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
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
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
import stack.commands
import stack.ip
import stack.text

class Command(stack.commands.HostArgumentProcessor,
	stack.commands.report.command):
	"""
	Output the DHCP server configuration file for a specific host.

	<arg optional='0' type='string' name='host' repeat='0'>
	Create a DHCP server configuration for the machine named 'host'. If
	no host name is supplied, then generate a DHCP configuration file
	for this host.
	</arg>

	<example cmd='report host dhcpd frontend-0-0'>
	Output the DHCP server configuration file for frontend-0-0.
	</example>
	"""


	def printHost(self, host, mac, ip, server, dev):
                """Write the host section of the dhcpd.conf."""

                self.addOutput('', '\thost %s.%s {' % (host, dev))
        	self.addOutput('', '\t\toption host-name "%s";' % host)
                
                subnet  = self.db.getHostAttr(host, 'network.private.subnet')
                netmask = self.db.getHostAttr(host, 'network.private.netmask')
                if subnet and netmask:
                	ipg = stack.ip.IPGenerator(subnet, netmask)
                	self.addOutput('', '\t\toption subnet-mask %s;' % netmask)
			self.addOutput('', '\t\toption broadcast-address %s;' %
                        	ipg.broadcast())

		gateway = None
		for (key, val) in self.db.getHostRoutes(host).items():
			if key == '0.0.0.0' and val[0] == '0.0.0.0':
				gateway = val[1]
                override = self.db.getHostAttr(host, 'network.private.gateway')
		if override:
			gateway = override
                if gateway:
			self.addOutput('', '\t\toption routers %s;' % gateway)

		self.addOutput('', '\t\thardware ethernet %s;' % mac)
		self.addOutput('', '\t\tfixed-address %s;' % ip)

		if self.str2bool(self.db.getHostAttr(host, 'kickstartable')):
			filename = self.db.getHostAttr(host, 'dhcp_filename')
			if filename:
				self.addOutput('', '\t\tfilename "%s";' %
                                               filename)

			nextserver = self.db.getHostAttr(host, 'dhcp_nextserver')
			if nextserver:
				self.addOutput('','\t\tserver-name "%s";'
					% nextserver)
				self.addOutput('','\t\tnext-server %s;'
					% nextserver)
                                
		self.addOutput('', '\t}')

		

	def writeDhcpDotConf(self, host):
		self.addOutput('', '<file name="/etc/dhcp/dhcpd.conf">')

                self.addOutput('', stack.text.DoNotEdit())

		rows = self.db.execute("""
                	select n.ip, s.subnet, s.netmask, s.dnszone from
                        networks n, subnets s, nodes nd where
                        n.node=nd.id and nd.name='%s' and
                        n.subnet=s.id and s.name='private'
                        """ % host)
                server, network, netmask, zone = self.db.fetchone()

		self.addOutput('', 'ddns-update-style none;')
		self.addOutput('', 'subnet %s netmask %s {'
			% (network, netmask))

		self.addOutput('', '\tdefault-lease-time 1200;')
		self.addOutput('', '\tmax-lease-time 1200;')

		ipg  = stack.ip.IPGenerator(network, netmask)
		self.addOutput('', '\toption subnet-mask %s;' % netmask)
		self.addOutput('', '\toption broadcast-address %s;' %
                               ipg.broadcast())
		self.addOutput('', '\toption domain-name-servers %s;' % server)
                
		
		self.db.execute("select name from nodes order by rack, rank")
		for name, in self.db.fetchall():

                        mac = None
                        ip  = None
                        dev = None
                        
			#
			# look for a physical private interface that has an
			# IP address assigned to it.
			#
			for (mac, ip, dev) in self.db.select("""
                        	n.mac, n.ip, n.device
                                from networks n, subnets s, nodes where
                                n.node = nodes.id and nodes.name = '%s' and
				s.name = 'private' and
				n.subnet = s.id and
				(n.vlanid is NULL or n.vlanid = 0)
                                """ % name):
                                pass

                        if ip: # nothing to write w/o an IP
                                
                        	if mac:
                                	self.printHost(name, mac, ip,
                                                       server, dev)
                                        
                                # add unasigned ethernet (not ib) macs
                                
                        	self.db.execute("""
                                	select n.mac, n.device
                                        from networks n, nodes where
                                        n.node = nodes.id and
                                        nodes.name = '%s' and
                                        ip is NULL
                                	""" % name)
                                
				for mac, dev in self.db.fetchall():
                        		if mac and len(mac.split(':')) == 6:
                                                self.printHost(name, mac, ip,
                                                               server, dev)

		self.addOutput('', '}')
		self.addOutput('', '</file>')



	def writeDhcpSysconfig(self):
		self.addOutput('', '<file name="/etc/sysconfig/dhcpd">')
                self.addOutput('', stack.text.DoNotEdit())

                fe_name = self.db.getHostname('localhost')

		rows = self.db.execute("""select device from networks,subnets
			where networks.node = (select id from nodes where
			name = '%s') and
			subnets.name = "private" and
			networks.subnet = subnets.id and
			networks.ip is not NULL and
			(networks.vlanid is NULL or
			networks.vlanid = 0)""" % (fe_name))

		if rows == 1:
			device, = self.db.fetchone()
		else:
			device = 'eth0'

		self.addOutput('', 'DHCPDARGS="%s"' % device)

		self.addOutput('', '</file>')
		



	def run(self, params, args):
		if len(args) > 1:
			self.abort('cannot supply more than one host name')
		if len(args) == 0:
			args = [ os.uname()[1] ]

		hosts = self.getHostnames(args)

		self.beginOutput()
		self.writeDhcpDotConf(hosts[0])
		self.writeDhcpSysconfig()
		self.endOutput(padChar='')


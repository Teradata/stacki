# @SI_Copyright@
#                               stacki.com
#                                  v3.3
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

import stack.commands
import re

class Command(stack.commands.list.host.command):
	"""
	Lists the interface definitions for hosts. For each host supplied on
	the command line, this command prints the hostname and interface
	definitions for that host.

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, info about
	all the known hosts is listed.
	</arg>

	<example cmd='list host interface compute-0-0'>
	List network interface info for compute-0-0.
	</example>

	<example cmd='list host interface'>
	List network interface info for all known hosts.
	</example>
	"""

	def run(self, params, args):

		expanded, = self.fillParams([ ('expanded', 'false') ])
                expanded = self.str2bool(expanded)

                networks = {}
                if expanded:
                        for row in self.call('list.network'):
                                networks[row['network']] = row
                        
                reg = re.compile('vlan.*')

                self.beginOutput()

                data = {}
                for host in self.getHostnames():
                        data[host] = []
                for row in self.db.select("""
                        distinctrow
                        n.name,
			IF(net.subnet, sub.name, NULL),
                        net.device, net.mac, net.main, net.ip,
                        net.module, net.name, net.vlanid, net.options,
                        net.channel
                        from
                        nodes n, networks net, subnets sub
                        where
                        net.node=n.id
                        and (net.subnet=sub.id or net.subnet is NULL)
                        order by net.device
                        """):
                        data[row[0]].append(row[1:])
                        
                for host in self.getHostnames(args):
#                        self.db.select("""distinctrow
#				IF(net.subnet, sub.name, NULL),
#				net.device, net.mac, net.main, net.ip,
#				net.module, net.name, net.vlanid, net.options,
#				net.channel
#				from nodes n, networks net, subnets sub
#				where n.name='%s' and net.node=n.id
#				and (net.subnet=sub.id or net.subnet is NULL)
#				order by net.device""" % host )

#			for (network,
#                             interface,
#                             mac,
#                             default,
#                             ip,
#                             module,
#                             name,
#                             vlan,
#                             options,
#                             channel) in self.db.fetchall():

			for (network,
                             interface,
                             mac,
                             default,
                             ip,
                             module,
                             name,
                             vlan,
                             options,
                             channel) in data[host]:

                		if interface and reg.match(interface):
                                        # If device name matches vlan*
                                        # Then clear fields for printing
                                        mac = ip = module = name = None

                                if not default:
                                        # Change False to None for easier
                                        # to read output.
                                        default = None
                                else:
                                        default = True

                                if not expanded:
                                        self.addOutput(host, (
                                                interface,
                                                default,
                                                network,
                                                mac,
                                                ip,
                                                name,
                                                module,
                                                vlan,
                                                options,
                                                channel
                                                ))
                                else:
					if network:
                                                mask = networks[network]['mask']
                                                gateway = networks[network]['gateway']
                                                zone = networks[network]['zone']
                                                dns = networks[network]['dns']
                                                pxe = networks[network]['pxe']
					else:
						mask = None
						gateway = None
						zone = None
						dns = None
						pxe = None
				
                                        self.addOutput(host, (
                                                interface,
                                                default,
                                                network,
                                                mac,
                                                ip,
                                                mask,
                                                gateway,
                                                name,
                                                zone,
                                                dns,
                                                pxe,
                                                module,
                                                vlan,
                                                options,
                                                channel
                                                ))

                if not expanded:
                        self.endOutput(header=[ 'host',
                                'interface',
                                'default',
                                'network',
                                'mac',
                                'ip',
                                'name',
                                'module',
                                'vlan',
                                'options',
                                'channel'
                                ])
                else:
                        self.endOutput(header=[ 'host',
                                'interface',
                                'default',
                                'network',
                                'mac',
                                'ip',
                                'mask',
                                'gateway',
                                'name',
                                'zone',
                                'dns',
                                'pxe',
                                'module',
                                'vlan',
                                'options',
                                'channel'
                                ])


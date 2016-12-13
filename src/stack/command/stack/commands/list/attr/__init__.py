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

import sys
import string
import fnmatch
import stack.attr
import stack.commands


class Command(stack.commands.Command):
	"""
	Lists the set of global attributes.

        <param type='string' name='attr'>
        A shell syntax glob pattern to specify to attributes to
        be listed.
        </param>

        <param type='boolean' name='shadow'>
        Specifies is shadow attributes are listed, the default
        is False.
        </param>

	<example cmd='list attr'>
	List the global attributes.
	</example>
	"""

        def get_global(self, objects):
                attrs    = self.get_attributes('global', None, objects)
                readonly = {}

                for (ip, host, subnet, netmask) in self.db.select(
                                """
				n.ip, if(n.name, n.name, nd.name), 
                                s.address, s.mask from 
                                networks n, appliances a, subnets s, nodes nd 
                                where 
                                n.node=nd.id and nd.appliance=a.id and 
                                a.name='frontend' and n.subnet=s.id and 
                                s.name='private'
                                """):
                        readonly['Kickstart_PrivateKickstartHost'] = ip
                        readonly['Kickstart_PrivateAddress'] = ip
                        readonly['Kickstart_PrivateHostname'] = host
                        ipg = stack.ip.IPGenerator(subnet, netmask)
                        readonly['Kickstart_PrivateBroadcast'] = '%s' % ipg.broadcast()

                for (ip, host, zone, subnet, netmask) in self.db.select(
                                """
                                n.ip, if(n.name, n.name, nd.name), 
                                s.zone, s.address, s.mask from 
                                networks n, appliances a, subnets s, nodes nd 
                                where 
                                n.node=nd.id and nd.appliance=a.id and
				a.name='frontend' and n.subnet=s.id and 
                                s.name='public'
                                """):
                        readonly['Kickstart_PublicAddress'] = ip
                        readonly['Kickstart_PublicHostname'] = '%s.%s' % (host, zone)
                        stack.ip.IPGenerator(subnet, netmask)
			readonly['Kickstart_PublicBroadcast'] = '%s' % ipg.broadcast()

                for (name, subnet, netmask, zone) in self.db.select(
                                """
                                name, address, mask, zone from 
                                subnets
				"""):
                        ipg = stack.ip.IPGenerator(subnet, netmask)
                        if name == 'private':
                                readonly['Kickstart_PrivateDNSDomain'] = zone
                                readonly['Kickstart_PrivateNetwork'] = subnet
                                readonly['Kickstart_PrivateNetmask'] = netmask
                                readonly['Kickstart_PrivateNetmaskCIDR'] = '%s' % ipg.cidr()
                        elif name == 'public':
                                readonly['Kickstart_PublicDNSDomain'] = zone
                                readonly['Kickstart_PublicNetwork'] = subnet
                                readonly['Kickstart_PublicNetmask'] = netmask
                                readonly['Kickstart_PublicNetmaskCIDR'] = 's' % ipg.cidr()

                readonly['release'] = stack.release
                readonly['version'] = stack.version

                for key in readonly:
                        attrs['global'][key] = (readonly[key], None, False)

                return attrs

        def get_os(self, oses):
                return self.get_attributes('os', None, oses)

        def get_environment(self, environments):
                return self.get_attributes('environment', None, environments)

        def get_appliance(self, appliances):
                return self.get_attributes('appliance', 'appliances', appliances)

        def get_host(self, hosts):
                attrs    = self.get_attributes('host', 'nodes', hosts)
                readonly = {}

                for (name, environment, rack, rank, cpus) in self.db.select(
                                """
                        	name,environment,rack,rank,cpus from nodes
                                """):
                        readonly[name]         = {}
                        readonly[name]['rack'] = rack
                        readonly[name]['rank'] = rank
                        readonly[name]['cpu']  = cpus
                        if environment:
                                readonly[name]['environment'] = environment

                for (name, box, appliance, longname) in self.db.select(
                                """ 
                                n.name, b.name,
                                a.name, a.longname from
                                nodes n, boxes b, appliances a where
                                n.appliance=a.id and n.box=b.id
                                """):

                        readonly[name]['box']                = box
                        readonly[name]['appliance']          = appliance
                        readonly[name]['appliance.longname'] = longname
                                
                for (name, zone, address) in self.db.select(
                                """
				n.name, s.zone, nt.ip from
				networks nt, nodes n, subnets s where
				nt.main=true and nt.node=n.id and
				nt.subnet=s.id
                                """):
                        readonly[name]['hostaddr']   = address
                        readonly[name]['domainname'] = zone

                for host in hosts:
                        readonly[host]['os']       = self.db.getHostOS(host)
                        readonly[host]['hostname'] = host


                for host in attrs:
                        host_attrs    = attrs[host]
                        host_readonly = readonly[host]

                        for key in host_readonly:
                                host_attrs[key] = (host_readonly[key], None, False)

                return attrs


        def get_attributes(self, scope, table=None, objects=None):
                attrs = {}
    		for object in objects:
                        attrs[object] = {}

                if scope == 'global':
                        shadow = """
                        scope, attr, value, shadow from attributes
                        where scope = 'global'
                        """
                        noshadow = """
                        scope, attr, value from attributes
                        where scope = 'global'
                        """
                else:
                        if table: # lookup requires a join
                                shadow = """
                                x.name, a.attr, a.value, a.shadow 
                                from attributes a, %s x where
                                a.scope = '%s' and a.pointerid = x.id
                                """ % (table, scope)
                                noshadow = """
                                x.name, a.attr, a.value
                                from attributes a, %s x where
                                a.scope = '%s' and a.pointerid = x.id
                                """ % (table, scope)
                        else:
                                shadow = """
                                pointerstr, attr, value, shadow
                                from attributes where
                                scope = '%s'
                                """ % scope
                                noshadow = """
                                pointerstr, attr, value
                                from attributes where
                                scope = '%s'
                                """ % scope

                rows = self.db.select(shadow)
                if not rows:
                        self.db.select(noshadow)

	        for row in rows:
		        if len(row) == 4:
			        (obj, a, v, x) = row
		        else:
			        x = None
			        (obj, a, v) = row
                        if attrs.has_key(obj):
			        attrs[obj][a] = (v, x, True)

                return attrs



	def run(self, params, args):

                (glob, shadow, scope) = self.fillParams([ 
                        ('attr',   None),
                        ('shadow', 'true'),
                        ('scope',  'global')
                ])

		shadow = self.str2bool(shadow)

                if scope == 'global':
                        objects		= [ 'global' ]
                        attributes	= self.get_global(objects)
                elif scope == 'os':
                        objects		= args
                        attributes	= self.get_os(objects)
                elif scope == 'environment':
                        objects		= args
                        attributes	= self.get_environment(objects)
                elif scope == 'appliance':
                        objects		= args
                        attributes	= self.get_appliance(objects)
                elif scope == 'host':
                        objects		= args
                        attributes	= self.get_host(objects)

                if glob:
                        for o in objects:
                                matches = {}
                                for key in fnmatch.filter(attributes[o].keys(), glob):
                                        matches[key] = attributes[o][key]
                                attributes[o] = matches

                self.beginOutput()

                objects.sort()
                for o in objects:
                        attrs = attributes[o]
                        keys  = attrs.keys()
                        keys.sort()
                        for a in keys:
                                (v, x, rw) = attrs[a]
                                if rw:
                                        internal = None
                                else:
                                        internal = True
                                attr  = a
                                value = v
                                if shadow and x:
                                        value = x

                                if scope == 'global':
                                        self.addOutput(attr, (internal, value))
                                else:
                                        self.addOutput(o, (attr, internal, value))
                                        

                if scope == 'global':
                        self.endOutput(header=['attr', 'internal', 'value' ])
                else:
                        self.endOutput(header=[scope, 'attr', 'internal', 'value' ])



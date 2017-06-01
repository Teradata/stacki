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

import sys
import string
import fnmatch
import ipaddress
import stack.attr
import stack.commands

class Command(stack.commands.Command,
              stack.commands.OSArgumentProcessor,
              stack.commands.ApplianceArgumentProcessor,
              stack.commands.EnvironmentArgumentProcessor,
              stack.commands.HostArgumentProcessor):
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

        def addGlobalAttrs(self, attributes):
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
                        ipnetwork = ipaddress.IPv4Network(unicode(
				subnet + '/' + netmask))
                        readonly['Kickstart_PrivateBroadcast'] = '%s' % ipnetwork.broadcast_address

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
                        ipnetwork = ipaddress.IPv4Network(unicode(
				subnet + '/' + netmask))
			readonly['Kickstart_PublicBroadcast'] = '%s' % ipnetwork.broadcast_address

                for (name, subnet, netmask, zone) in self.db.select(
                                """
                                name, address, mask, zone from 
                                subnets
				"""):
                        ipnetwork = ipaddress.IPv4Network(unicode(
				subnet + '/' + netmask))
                        if name == 'private':
                                readonly['Kickstart_PrivateDNSDomain'] = zone
                                readonly['Kickstart_PrivateNetwork'] = subnet
                                readonly['Kickstart_PrivateNetmask'] = netmask
                                readonly['Kickstart_PrivateNetmaskCIDR'] = '%s' % ipnetwork.prefixlen
                        elif name == 'public':
                                readonly['Kickstart_PublicDNSDomain'] = zone
                                readonly['Kickstart_PublicNetwork'] = subnet
                                readonly['Kickstart_PublicNetmask'] = netmask
                                readonly['Kickstart_PublicNetmaskCIDR'] = '%s' % ipnetwork.prefixlen

                readonly['release'] = stack.release
                readonly['version'] = stack.version

                for key in readonly:
                        attributes['global'][key] = (readonly[key], None, 'const', 'global')

                return attributes


        def addHostAttrs(self, attributes):
                readonly = {}

                boxes = {}
                for row in self.call('list.box'):
                        boxes[row['name']] = { 'pallets': row['pallets'].split(),
                                               'carts'  : row['carts'].split() }

                for (name, environment, rack, rank) in self.db.select(
                                """
                        	n.name, e.name, n.rack, n.rank 
                                from nodes n
                                left join environments e on n.environment=e.id
                                """):
                        readonly[name]         = {}
                        readonly[name]['rack'] = rack
                        readonly[name]['rank'] = rank
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
                        readonly[name]['pallets']            = boxes[box]['pallets']
                        readonly[name]['carts']              = boxes[box]['carts']
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

                for host in readonly:
                        readonly[host]['os']       = self.db.getHostOS(host)
                        readonly[host]['hostname'] = host


                for host in attributes:
                        a = attributes[host]
                        r = readonly[host]

                        for key in r:
                                a[key] = (r[key], None, 'const', 'host')

                return attributes




	def run(self, params, args):

                (glob, shadow, scope, resolve, var, const) = self.fillParams([ 
                        ('attr',   None),
                        ('shadow', True),
                        ('scope',  'global'),
                        ('resolve', None),
                        ('var', True),
                        ('const', True)
                ])

		shadow  = self.str2bool(shadow)
                var     = self.str2bool(var)
                const   = self.str2bool(const)
                lookup  = { 'global'     : { 'fn'     : lambda x=None: [ 'global' ],
                                             'const'  : self.addGlobalAttrs,
                                             'resolve': False,
                                             'table'  : None },
                            'os'         : { 'fn'     : self.getOSNames,
                                             'const'  : lambda x: x,
                                             'resolve': False,
                                             'table'  : 'oses' },
                            'appliance'  : { 'fn'     : self.getApplianceNames, 
                                             'const'  : lambda x: x,
                                             'resolve': False,
                                             'table'  : 'appliances' },
                            'environment': { 'fn'     : self.getEnvironmentNames,
                                             'const'  : lambda x: x,
                                             'resolve': False,
                                             'table'  : 'environments' },
                            'host'       : { 'fn'     : self.getHostnames,
                                             'const'  : self.addHostAttrs,
                                             'resolve': True,
                                             'table'  : 'nodes' }}

                if scope not in lookup.keys():
                        raise CommandError(self, 'invalid scope "%s"' % scope)

                if resolve == None:
                        resolve = lookup[scope]['resolve']
                else:
                        resolve = self.str2bool(resolve)

                attributes = {}
                for s in lookup.keys():
                        attributes[s] = {}
                        for target in lookup[s]['fn']():
                                attributes[s][target] = {}

                        if var:
                                table = lookup[s]['table']
                                if table:
                                        rows = self.db.select("""
                        			t.name, a.attr, a.value, a.shadow 
	                                	from attributes a, %s t where
	        	                        a.scope = '%s' and a.scopeid = t.id
                	                	""" % (table, s))
                                        if rows:
                                                for (o, a, v, x) in rows:
                                                        attributes[s][o][a] = (v, x, 'var', s)
                                        else:
                                                for (o, a, v) in self.db.select("""
	                                		t.name, a.attr, a.value
		        	                        from attributes a, %s t where
        		        	                a.scope = '%s' and a.scopeid = t.id
                		        	        """ % (table, s)):
                                                        attributes[s][o][a] = (v, None, 'var', s)

	                        else:
        	                        o = target
                	                rows = self.db.select("""
                        	        	attr, value, shadow from attributes
	                        	        where scope = '%s'
	        	                        """ % s)
        	                        if rows:
                	                	for (a, v, x) in rows:
                        	                        attributes[s][o][a] = (v, x, 'var', s)
	                                else:
        	                                for (a, v) in self.db.select("""
                	                		attr, value from attributes
	                	                	where scope = '%s'
	                        	        	""" % s):
	                                	        attributes[s][o][a] = (v, None, 'var', s)

                        if const:
                                # Mix in any const attributes
                                lookup[s]['const'](attributes[s])


                targets = lookup[scope]['fn'](args)
                targets.sort()

                if resolve and scope == 'host':
			for o in targets:
				env = self.db.getHostEnvironment(o)
				if env:
					parent = attributes['environment'][env]
					for (a, (v, x, t, s)) in parent.items():
						if not attributes[scope][o].has_key(a):
							attributes[scope][o][a] = (v, x, t, s)

				parent = attributes['appliance'][self.db.getHostAppliance(o)]
				for (a, (v, x, t, s)) in parent.items():
					if not attributes[scope][o].has_key(a):
						attributes[scope][o][a] = (v, x, t, s)

				parent = attributes['os'][self.db.getHostOS(o)]
				for (a, (v, x, t, s)) in parent.items():
					if not attributes[scope][o].has_key(a):
						attributes[scope][o][a] = (v, x, t, s)

                if resolve and scope != 'global':
                        for o in targets:
                                for (a, (v, x, t, s)) in attributes['global']['global'].items():
                                	if not attributes[scope][o].has_key(a):
                                                attributes[scope][o][a] = (v, x, t, s)

                if glob:
                        for o in targets:
                                matches = {}
                                for key in fnmatch.filter(attributes[scope][o].keys(), glob):
                                        matches[key] = attributes[scope][o][key]
                                attributes[scope][o] = matches


                        

                self.beginOutput()

                for o in targets:
                        attrs = attributes[scope][o]
                        keys  = attrs.keys()
                        keys.sort()
                        for a in keys:
                                (v, x, t, s) = attrs[a]
                                if x:
                                        t = 'shadow'
                                        if shadow:
                                                v = x
                                if scope == 'global':
                                        self.addOutput(s, (t, a, v))
                                else:
                                        self.addOutput(o, (s, t, a, v))
                                        
                if scope == 'global':
                        self.endOutput(header=['scope', 'type', 'attr', 'value' ])
                else:
                        self.endOutput(header=[scope, 'scope', 'type', 'attr', 'value' ])



RollName = "stacki"

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

import stack.commands

class Command(stack.commands.list.host.command):
	"""
	Lists the set of attributes for hosts.

	<arg optional='1' type='string' name='host'>
	Host name of machine
	</arg>
	
        <param type='string' name='attr'>
        A shell syntax glob pattern to specify to attributes to
        be listed.
        </param>

	<example cmd='list host attr backend-0-0'>
	List the attributes for backend-0-0.
	</example>
	"""

	def run(self, params, args):

                (resolve, ) = self.fillParams([('resolve', 'true')])
                resolve     = self.str2bool(resolve)
                hosts       = self.getHostnames(args)

                argv = []
                for p in params:
                        if not p in ['resolve']:
                                argv.append('%s=%s' % (p, params[p]))

                hostAttrs = {}
                hosts.sort()
                for host in hosts:
                        hostAttrs[host] = {}

                for row in self.call('list.attr', hosts + ['scope=host'] + argv):
                        hostAttrs[row['host']][row['attr']] = ('host', 
                                                               row['value'], 
                                                               row['internal'])

                for host in hosts:

                        attrs = {}
                        if resolve:

                                # Global Attributes

                                for row in self.call('list.attr', argv):
                                        attrs[row['attr']] = ('global', 
                                                              row['value'], 
                                                              row['internal'])

                                # OS Attributes

                                for row in self.call('list.attr', 
                                                     ['%s' % self.db.getHostOS(host), 
                                                      'scope=os'] + argv):
                                        attrs[row['attr']] = ('os', 
                                                              row['value'], 
                                                              row['internal'])

                                # Appliance Attributes

                                for row in self.call('list.attr', 
                                                     ['%s' % self.db.getHostAppliance(host), 
                                                      'scope=appliance'] + argv):
                                        attrs[row['attr']] = ('appliance', 
                                                              row['value'], 
                                                              row['internal'])

                                # Environment Attributes

                                env = self.db.getHostEnvironment(host)
                                if env:
                                        for row in self.call('list.attr', 
                                                             ['%s' % env, 
                                                              'scope=environment'] + argv):
                                                attrs[row['attr']] = ('environment', 
                                                                      row['value'], 
                                                                      row['internal'])
                                        
                        for key in attrs:
                                if not key in hostAttrs[host]:
                                        hostAttrs[host][key] = attrs[key]

                self.beginOutput()

                for host in hosts:
                        attrs = hostAttrs[host]
                        keys  = attrs.keys()
                        keys.sort()
                        for a in keys:
                                (s, v, i) = attrs[a]
                                if resolve:
                                        self.addOutput(host, (a, s, i, v))
                                else:
                                        self.addOutput(host, (a, i, v))

                if resolve:
                        self.endOutput(header=['host', 'attr', 'scope', 'internal', 'value' ])
                else:
                        self.endOutput(header=['host', 'attr', 'internal', 'value' ])



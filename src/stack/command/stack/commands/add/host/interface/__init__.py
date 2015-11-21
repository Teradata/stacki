# @SI_Copyright@
#                             www.stacki.com
#                                  v2.0
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
import stat
import time
import sys
import string
import stack.commands
from stack.exception import *

class Command(stack.commands.add.host.command):
	"""
	Adds an interface to a host and sets the associated values.

	<arg type='string' name='host'>
	Host name of machine
	</arg>
	
	<param type='string' name='interface'>
	The interface name on the host (e.g., 'eth0', 'eth1')
	</param>

	<param type='string' name='ip'>
	The IP address to assign to the interface (e.g., '192.168.1.254')
	</param>

	<param type='string' name='network'>
	The name of the network to assign to the interface (e.g., 'private')
	</param>
	
	<param type='string' name='name'>
	The name to assign to the interface
	</param>
	
	<param type='string' name='mac'>
	The MAC address of the interface (e.g., '00:11:22:33:44:55')
	</param>
	
	<param type='string' name='module'>
	The device driver name (or module) of the interface (e.g., 'e1000')
	</param>

	<param type='string' name='vlan'>
	The VLAN ID to assign the interface
	</param>

	<example cmd='add host interface backend-0-0 interface=eth1 ip=192.168.1.2 network=private name=fast-0-0'>
	Add interface "eth1" to host "backend-0-0" with the given
	IP address, network assignment, and name.
	</example>
	"""

	def run(self, params, args):

		hosts = self.getHostnames(args)
                (interface, mac) = self.fillParams([
                        ('interface', None),
                        ('mac',       None)
                        ])

		if not interface and not mac:
                        raise ParamRequired(self, ('interface', 'mac'))
		if len(hosts) != 1:
                        raise ArgUnique(self, 'host')

		host = hosts[0]

                for dict in self.call('list.host.interface', [ host ]):
                        if interface == dict['interface']:
                                raise CommandError(self, 'interface exists')
                        if mac == dict['mac']:
                                raise CommandError(self, 'mac exists')


		fields = [ 'network', 'ip', 'module', 'name', 'vlan', 'default']

                # Insert the mac or interface into the database and then use
                # that to key off of for all the subsequent fields.
                # Give the MAC preferrence (need to pick one) but still do the
                # right thing when MAC and Interface are both specified.
                
                if mac:
			self.db.execute("""
                        	insert into networks(node, mac)
				values ((select id from nodes where name='%s'), '%s')
                                """ % (host, mac)) 
                        handle = 'mac=%s' % mac
                        fields.append('interface')
		else:
			self.db.execute("""
                        	insert into networks(node, device)
				values ((select id from nodes where name='%s'), '%s')
                                """ % (host, interface)) 
                        handle = 'interface=%s' % interface
                        fields.append('mac')

		for key in fields:
			if key in params:
				self.command('set.host.interface.%s' % key,
					(host, handle, "%s=%s" % (key, params[key])))


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
import sys
import types
import string
import ipaddress
import stack.commands
from stack.exception import *

class Command(stack.commands.add.command):
	"""
	Add a network to the database. By default,
	the "private" network is already defined.

	<arg name='name'>
	Name of the new network.
	</arg>
	
	<param name='address' optional='0'>
        Network address.
	</param>
	
	<param name='mask' optional='0'>
        Network mask.
	</param>

        <param name='gateway'>
        Default gateway for the network. This is optional, not all networks
        require gateways.
        </param>
	
	<param name='mtu'>
	The MTU for the new network. Default is 1500.
	</param>

	<param name='zone'>
	The Domain name or the DNS Zone name to use
	for all hosts of this particular subnet. Default
	is set to the name of the network.
	</param>
	
	<param type='boolean' name='dns'>
        If set to True this network will be included in the builtin DNS server.
        The default value is false.
	</param>

	<param type='boolean' name='pxe'>
        If set to True this network will be managed by the builtin DHCP/PXE
        server.
        The default is False.
	</param>
	"""

        def run(self, params, args):

        	if len(args) != 1:
                        raise ArgUnique(self, 'network')
        	name = args[0]
        	
		(address, mask, gateway,
                         mtu, zone, dns, pxe) = self.fillParams([
                                 ('address',	None, True),
                                 ('mask',	None, True),
                                 ('gateway',	None),
                                 ('mtu',       '1500'),
                                 ('zone',	name),
                                 ('dns',	'n'),
                                 ('pxe',	'n')
                                 ])

		dns = self.str2bool(dns)
                pxe = self.str2bool(pxe)

		# Insert the name of the new network into the subnets
		# table if it does not already exist
			
		rows = self.db.select("""
        		* from subnets where name='%s'
        		""" % name)
		if len(rows):
			raise CommandError(self, 'network "%s" exists' % name)

		try:
			if ipaddress.IPv4Network(u"%s/%s" % (address, mask)):
				pass
		except:
			msg = '%s/%s is not a valid network address and subnet mask combination'
			raise CommandError(self, msg % (address, mask))

		self.db.execute("""
			insert into subnets 
        		(name, address, mask, gateway, mtu, zone, dns, pxe)
                	values 
        		('%s', '%s', '%s', '%s', '%s', '%s', %s, %s)
        		""" % (name, address, mask, gateway, mtu, zone, dns, pxe))

# @SI_Copyright@
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

class Command(stack.commands.set.host.command):
	"""
	Sets the logical name of a network interface on a particular host.

	<arg type='string' name='host'>
	Host name.
	</arg>
	
	<arg type='string' name='interface'>
 	Interface that should be updated. This may be a logical interface or 
 	the MAC address of the interface.
 	</arg>
 	
 	<arg type='string' name='name'>
	Name of this interface (e.g. newname). This is only the
	name associated with a certain interface. FQDNs are disallowed.
	To set the domain or zone for an interface, use the
	"rocks add network" command, and then associate the interface
	with the network
	</arg>

	<param type='string' name='interface'>
	Can be used in place of the interface argument.
	</param>

	<param type='string' name='name'>
	Can be used in place of the name argument. 
	</param>
	

	<example cmd='set host interface name backend-0-0 eth1 cluster-0-0'>
	Sets the name for the eth1 device on host backend-0-0 to
	cluster-0-0.zonename. The zone is decided by the subnet that the
	interface is attached to.
	</example>

	<example cmd='set host interface name backend-0-0 interface=eth1 name=c0-0'>
	Same as above.
	</example>
	
	<!-- cross refs do not exist yet
	<related>set host interface interface</related>
	<related>set host interface ip</related>
	<related>set host interface module</related>
	-->
	<related>add host</related>
	<related>add network</related>
	"""
	
	def run(self, params, args):

		(args, interface, name) = self.fillPositionalArgs(('interface','name'))

		hosts = self.getHostnames(args)	
			
		if len(hosts) != 1:
			self.abort('must supply one host')

		# One host only
		host = hosts[0]

		if not interface:
			self.abort('must supply interface')
		if not name:
			self.abort('must supply name')

		if len(name.split('.')) > 1:
			self.abort('cannot be fqdn\n' +\
			'Please use subnets table to set domain name')

		if name.upper() == "NULL":
			name = host

		self.db.execute("""update networks, nodes set 
			networks.name='%s' where nodes.name='%s'
			and networks.node=nodes.id and
			(networks.device='%s' or networks.mac='%s')""" %
			(name, host, interface, interface))


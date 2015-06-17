# $Id$
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
#
# $Log$
# Revision 1.9  2010/09/07 23:52:50  bruno
# star power for gb
#
# Revision 1.8  2010/07/09 22:30:56  bruno
# gateway can't be NULL
#
# Revision 1.7  2010/05/20 00:31:44  bruno
# gonna get some serious 'star power' off this commit.
#
# put in code to dynamically configure the static-routes file based on
# networks (no longer the hardcoded 'eth0').
#
# Revision 1.6  2010/01/14 23:42:30  bruno
# added 'host' argument to help section
#
# Revision 1.5  2009/07/21 21:50:51  bruno
# fix help
#
# Revision 1.4  2009/05/01 19:06:55  mjk
# chimi con queso
#
# Revision 1.3  2009/03/13 19:44:09  mjk
# - added add.appliance.route
# - added add.os.route
#
# Revision 1.1  2009/03/13 17:58:15  mjk
# *** empty log message ***
#


import stack.commands

class Command(stack.commands.add.host.command):
	"""
	Add a route for a host

	<arg type='string' name='host'>
	Host name of machine
	</arg>
	
	<param type='string' name='address'>
	Host or network address
	</arg>
	
	<param type='string' name='gateway'>
	Network or device gateway
	</arg>

	<param type='string' name='netmask'>
	Specifies the netmask for a network route.  For a host route
	this is not required and assumed to be 255.255.255.255
	</param>
	"""

	def run(self, params, args):

		(args, address, gateway) = self.fillPositionalArgs(
			('address','gateway'))

		(netmask,) = self.fillParams([('netmask', '255.255.255.255')])
		
		hosts = self.getHostnames(args)
		
		if not address:
			self.abort('address required')
		if not gateway:
			self.abort('gateway required')

		#
		# determine if this is a subnet identifier
		#
		subnet = 0
		rows = self.db.execute("""select id from subnets where
			name = '%s' """ % gateway)

		if rows == 1:
			subnet, = self.db.fetchone()
			gateway = "''"
		else:
			subnet = 'NULL'
			gateway = "'%s'" % gateway
		
		# Verify the route doesn't already exist.  If it does
		# for any of the hosts abort.
		
		for host in hosts:
			rows = self.db.execute("""select * from 
				node_routes r, nodes n where
				r.node=n.id and r.network='%s' 
				and n.name='%s'""" %	
				(address, host)) 
			if rows:
				self.abort('route exists')
		
		# Now that we know things will work insert the route for
		# all the hosts
		
		for host in hosts:	
			self.db.execute("""insert into node_routes values 
				((select id from nodes where name='%s'),
				'%s', '%s', %s, %s)""" %
                	        (host, address, netmask, gateway, subnet))


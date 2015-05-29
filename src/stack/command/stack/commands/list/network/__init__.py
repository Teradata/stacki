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
# Revision 1.11  2010/09/07 23:52:56  bruno
# star power for gb
#
# Revision 1.10  2010/06/30 17:37:33  anoop
# Overhaul of the naming system. We now support
# 1. Multiple zone/domains
# 2. Serving DNS for multiple domains
# 3. No FQDN support for network names
#    - FQDN must be split into name & domain.
#    - Each piece information will go to a
#      different table
# Hopefully, I've covered the basics, and not broken
# anything major
#
# Revision 1.9  2009/06/03 21:28:52  bruno
# add MTU to the subnets table
#
# Revision 1.8  2009/05/01 19:06:59  mjk
# chimi con queso
#
# Revision 1.7  2008/10/18 00:55:54  mjk
# copyright 5.1
#
# Revision 1.6  2008/03/06 23:41:38  mjk
# copyright storm on
#
# Revision 1.5  2007/07/04 01:47:38  mjk
# embrace the anger
#
# Revision 1.4  2007/06/28 19:51:42  bruno
# help for 'rocks list network'
#
# Revision 1.3  2007/06/19 16:42:42  mjk
# - fix add host interface docstring xml
# - update copyright
#
# Revision 1.2  2007/06/12 01:33:40  mjk
# - added NetworkArgumentProcessor
# - updated rocks list network
#
# Revision 1.1  2007/06/12 01:10:42  mjk
# - 'rocks add subnet' is now 'rocks add network'
# - added set network subnet|netmask
# - added list network
# - other cleanup
#


import os
import stat
import time
import sys
import string
import stack.commands


class Command(stack.commands.NetworkArgumentProcessor,
	stack.commands.list.command):
	"""
	List the defined networks for this system.

	<arg optional='1' type='string' name='network' repeat='1'>
	Zero, one or more network names. If no network names are supplied,
	info about all the known networks is listed.
	</arg>
	
	<example cmd='list network private'>
	List network info for the network named 'private'.
	</example>

	<example cmd='list network'>
	List info for all defined networks.
	</example>
	"""

	def run(self, params, args):
		
		self.beginOutput()
		
		for net in self.getNetworkNames(args):
			self.db.execute("""select subnet, netmask, mtu, 
				dnszone, if(servedns,'True','False')
				from subnets where name='%s'""" % net)
			for row in self.db.fetchall():
				self.addOutput(net, row)
			
		self.endOutput(header=['network', 'subnet', 'netmask', 'mtu', 'dnszone', 'servedns'])

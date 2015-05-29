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
# Revision 1.12  2010/09/07 23:53:01  bruno
# star power for gb
#
# Revision 1.11  2009/05/01 19:07:03  mjk
# chimi con queso
#
# Revision 1.10  2008/10/18 00:55:57  mjk
# copyright 5.1
#
# Revision 1.9  2008/03/06 23:41:39  mjk
# copyright storm on
#
# Revision 1.8  2007/07/05 17:46:45  bruno
# fixes
#
# Revision 1.7  2007/07/04 02:14:35  mjk
# fix docstring
#
# Revision 1.6  2007/07/04 01:47:39  mjk
# embrace the anger
#
# Revision 1.5  2007/06/29 21:22:05  bruno
# more cleanup
#
# Revision 1.4  2007/06/19 16:42:43  mjk
# - fix add host interface docstring xml
# - update copyright
#
# Revision 1.3  2007/06/12 19:15:11  mjk
# - simpler set network commands
# - added remove network
#
# Revision 1.2  2007/06/12 01:10:42  mjk
# - 'rocks add subnet' is now 'rocks add network'
# - added set network subnet|netmask
# - added list network
# - other cleanup
#
# Revision 1.1  2007/06/08 03:26:24  mjk
# - plugins call self.owner.addText()
# - non-existant bug was real, fix plugin graph stuff
# - add set host cpus|membership|rack|rank
# - add list host (not /etc/hosts, rather the nodes table)
# - fix --- padding for only None fields not 0 fields
# - list host interfaces is cool works for incomplete hosts
#

import stack.commands

class Command(stack.commands.set.host.command):
	"""
	Set the number of CPUs for a list of hosts.
	
	<arg type='string' name='host' repeat='1'>
	One or more host names.
	</arg>

	<arg type='string' name='cpus'>
	The number of CPUs to assign to each host.
	</arg>

	<param optional='1' type='string' name='cpus'>
	Can be used in place of the cpus argument.
	</param>

	<example cmd='set host cpus compute-0-0 2'>
	Sets the CPU value to 2 for compute-0-0.
	</example>

	<example cmd='set host cpus compute-0-0 compute-0-1 4'>
	Sets the CPU value to 4 for compute-0-0 and compute-0-1.
	</example>

	<example cmd='set host cpus compute-0-0 compute-0-1 cpus=4'>
	Same as above.
	</example>
	"""

	def run(self, params, args):
		(args, cpus) = self.fillPositionalArgs(('cpus',))
		
		if not len(args):
			self.abort('must supply host')
		if not cpus:
			self.abort('must supply cpus')
			
		for host in self.getHostnames(args):
			self.db.execute("""update nodes set cpus=%d where
				name='%s'""" % (int(cpus), host))
		

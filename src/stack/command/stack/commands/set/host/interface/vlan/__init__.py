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
# Revision 1.6  2010/09/07 23:53:01  bruno
# star power for gb
#
# Revision 1.5  2009/07/28 17:52:20  bruno
# be consistent -- all references to 'vlanid' should be 'vlan'
#
# Revision 1.4  2009/05/01 19:07:03  mjk
# chimi con queso
#
# Revision 1.3  2009/01/08 01:20:57  bruno
# for anoop
#
# Revision 1.2  2008/10/18 00:55:57  mjk
# copyright 5.1
#
# Revision 1.1  2008/07/22 00:34:41  bruno
# first whack at vlan support
#
#
#

import stack.commands

class Command(stack.commands.set.host.command):
	"""
	Sets the VLAN ID for an interface on one of more hosts. 

	<arg type='string' name='host' repeat='1'>
	One or more named hosts.
	</arg>
	
	<arg type='string' name='iface'>
 	Interface that should be updated. This may be a logical interface or 
 	the mac address of the interface.
 	</arg>

	<arg type='string' name='vlan'>
	The VLAN ID that should be updated. This must be an integer and the
	pair 'subnet/vlan' must be defined in the VLANs table.
 	</arg>
 	
	<param type='string' name='iface'>
	Can be used in place of the iface argument.
	</param>

	<param type='string' name='vlan'>
	Can be used in place of the vlan argument.
	</param>

	<example cmd='set host interface vlan compute-0-0-0 eth0 3'>
	Sets compute-0-0-0's private interface to VLAN ID 3.
	</example>

	<example cmd='set host interface vlan compute-0-0-0 subnet=eth0 vlan=3
'>
	Same as above.
	</example>
	
	<related>add host</related>
	"""
	
	def run(self, params, args):

		(args, iface, vid) = self.fillPositionalArgs(
			('iface', 'vlan'))

		if not len(args):
			self.abort('must supply host')

		if not iface:
			self.abort('must supply iface')

		if not vid:
			self.abort('must supply vlan')
		else:
			try:
				vlanid = int(vid)
			except:
				self.abort('vlan "%s" must be an integer' %
					(vid))

		for host in self.getHostnames(args):
			self.db.execute("""update networks net, nodes n
				set net.vlanid = IF(%d = 0, NULL, %d)
				where net.device = '%s' and
				n.name = '%s' and net.node = n.id""" %
				(vlanid, vlanid, iface, host))


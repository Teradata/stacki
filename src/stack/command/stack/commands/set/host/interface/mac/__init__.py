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
# Revision 1.13  2010/09/07 23:53:01  bruno
# star power for gb
#
# Revision 1.12  2009/05/01 19:07:03  mjk
# chimi con queso
#
# Revision 1.11  2009/04/14 16:12:17  bruno
# push towards chimmy beta
#
# Revision 1.10  2008/10/18 00:55:57  mjk
# copyright 5.1
#
# Revision 1.9  2008/03/06 23:41:40  mjk
# copyright storm on
#
# Revision 1.8  2007/07/04 01:47:39  mjk
# embrace the anger
#
# Revision 1.7  2007/06/19 16:42:43  mjk
# - fix add host interface docstring xml
# - update copyright
#
# Revision 1.6  2007/06/18 20:18:52  phil
# Updates to allow NULL setting
# Rationalize command naming conventions
#
# Revision 1.5  2007/06/18 15:40:09  phil
# set mac=NULL to clear the mac address
#
# Revision 1.4  2007/06/16 23:49:20  phil
# Add some helper functions for parameter,argument processing when wanting to
# support named arguments.   Cleaned up set host interface mac
#
# Revision 1.3  2007/06/16 02:39:51  mjk
# - added list roll commands (used for docbook)
# - docstrings should now be XML
# - added parser for docstring to ASCII or DocBook
# - ditched Phil's Network regex stuff (will come back later)
# - updated several docstrings
#
# Revision 1.2  2007/06/16 00:15:46  phil
# a fill positional parameters. Phil needs python help from katz
#
# Revision 1.1  2007/06/15 20:52:02  phil
# Set the mac address of a particular interface
#

import stack.commands

class Command(stack.commands.set.host.command):
	"""
	Sets the mac address for named interface on host.

	<arg type='string' name='host'>
	Host name.
	</arg>
	
	<arg type='string' name='iface'>
 	Interface that should be updated. This may be a logical interface or 
 	the mac address of the interface.
 	</arg>
 	
 	<arg type='string' name='mac'>
	The mac address of the interface. Usually of the form dd:dd:dd:dd:dd:dd
	where d is a hex digit. This format is not enforced. Use mac=NULL to
	clear the mac address.
	</arg>

	<param type='string' name='iface'>
	Can be used in place of the iface argument.
	</param>

	<param type='string' name='mac'>
	Can be used in place of the mac argument.
	</param>
	

	<example cmd='set host interface mac compute-0-0 eth1 00:0e:0c:a7:5d:ff'>
	Sets the MAC Address for the eth1 device on host compute-0-0.
	</example>

	<example cmd='set host interface mac compute-0-0 iface=eth1 mac=00:0e:0c:a7:5d:ff'>
	Same as above.
	</example>
	
	<example cmd='set host interface mac compute-0-0 iface=eth1 mac=NULL'>
	clears the mac address from the database
	</example>
	
	<!-- cross refs do not exist yet
	<related>set host interface iface</related>
	<related>set host interface ip</related>
	<related>set host interface module</related>
	-->
	<related>add host</related>
	"""
	
	def run(self, params, args):

		(args, iface, mac) = self.fillPositionalArgs(('iface', 'mac'))

		hosts = self.getHostnames(args)	
			
		if len(hosts) != 1:
			self.abort('must supply one host')
		if not iface:
			self.abort('must supply iface')
		if not mac:
			self.abort('must supply mac')

		for host in hosts:
			self.db.execute("""update networks, nodes set 
				networks.mac=NULLIF('%s','NULL') where
				nodes.name='%s' and networks.node=nodes.id and
				(networks.device='%s' or networks.mac='%s')""" %
				(mac, host, iface, iface))


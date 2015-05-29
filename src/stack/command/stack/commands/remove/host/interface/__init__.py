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
# Revision 1.14  2011/01/27 20:06:14  bruno
# when an interface is removed from the database, also try to remove the
# ifcfg-* file on the node
#
# Revision 1.13  2010/09/07 23:52:58  bruno
# star power for gb
#
# Revision 1.12  2009/05/01 19:07:00  mjk
# chimi con queso
#
# Revision 1.11  2008/10/18 00:55:56  mjk
# copyright 5.1
#
# Revision 1.10  2008/03/06 23:41:38  mjk
# copyright storm on
#
# Revision 1.9  2008/02/01 20:50:54  bruno
# add the ability to remove all interface with a wildcard
#
# Revision 1.8  2007/07/04 01:47:39  mjk
# embrace the anger
#
# Revision 1.7  2007/06/26 18:28:07  bruno
# 'remove host interface' now looks like 'set host interface'
#
# Revision 1.6  2007/06/25 23:45:06  bruno
# associate with base roll
#
# Revision 1.5  2007/06/19 16:42:42  mjk
# - fix add host interface docstring xml
# - update copyright
#
# Revision 1.4  2007/06/05 22:28:11  mjk
# require root for all remove commands
#
# Revision 1.3  2007/05/31 19:35:43  bruno
# first pass at getting all the 'help' consistent on all the rocks commands
#
# Revision 1.2  2007/05/10 20:37:02  mjk
# - massive rocks-command changes
# -- list host is standardized
# -- usage simpler
# -- help is the docstring
# -- host groups and select statements
# - added viz commands
#
# Revision 1.1  2007/04/18 22:03:44  bruno
# commands to add/remove host interfaces is now:
#
#     rocks add host interface
#     rocks remove host interface
#
# Revision 1.1  2007/04/18 22:00:11  bruno
# remove interfaces from the new rocks command line
#
#


import os
import stat
import time
import sys
import string
import stack.commands
import threading

class Command(stack.commands.remove.host.command):
	"""
	Remove a network interface definition for a host.

	<arg type='string' name='host'>
	One or more named hosts.
	</arg>
	
	<arg type='string' name='iface'>
 	Interface that should be removed. This may be a logical interface or 
 	the mac address of the interface.
 	</arg>
 	
	<param type='string' name='iface'>
	Can be used in place of the iface argument.
	</param>

	<example cmd='remove host interface compute-0-0 eth1'>
	Removes the interface eth1 on host compute-0-0.
	</example>

	<example cmd='remove host interface compute-0-0 compute-0-1 iface=eth1'>
	Removes the interface eth1 on hosts compute-0-0 and compute-0-1.
	</example>
	"""

	def run(self, params, args):
		(args, iface) = self.fillPositionalArgs(('iface', ))
	
		if not len(args):
			self.abort('must supply host')
		if not iface:
			self.abort('must supply iface')
			
		hosts = self.getHostnames(args)

		for host in hosts:
			self.db.execute("""delete from networks where 
				node=(select id from nodes where name='%s')
				and (device like '%s' or mac like '%s')""" % 
				(host, iface, iface))

#		I was shocked to see this here, also caused issues if the
#		host doesn't exist. -mjk
#			
#		cmd = 'rm -f /etc/sysconfig/network-scripts/ifcfg-%s' % iface
#		self.command('run.host', hosts + [ cmd ] )

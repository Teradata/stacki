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
# Revision 1.12  2010/09/07 23:52:58  bruno
# star power for gb
#
# Revision 1.11  2009/05/01 19:07:00  mjk
# chimi con queso
#
# Revision 1.10  2008/10/18 00:55:56  mjk
# copyright 5.1
#
# Revision 1.9  2008/03/06 23:41:39  mjk
# copyright storm on
#
# Revision 1.8  2007/07/04 01:47:39  mjk
# embrace the anger
#
# Revision 1.7  2007/06/28 21:48:38  bruno
# made a sweep over all the remove commands
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
# Revision 1.1  2007/04/24 17:58:09  bruno
# consist look and feel for all 'list' commands
#
# put partition commands under 'host'
#
# Revision 1.1  2007/04/05 20:51:55  bruno
# rocks-partition is now in the command line
#
#

import sys
import socket
import stack.commands
import string

class Command(stack.commands.remove.host.command):
	"""
	Remove a partition definitions from a host.

	<arg type='string' name='host' repeat='1'>
	A list of one or more host names.
	</arg>

	<param type='string' name='partition'>
	A single partition to remove from this host. If no partition is
	specified, then all partitions from the host are removed.
	</param>

	<param name="device" type="string">
	Device name to be removed
	</param>

	<param name="uuid" type="string">
	UUID of the mountpoint to be removed.
	</param>

	<example cmd='remove host partition compute-0-0'>
	Remove all partitions from compute-0-0.
	</example>

	<example cmd='remove host partition compute-0-0 partition=/export'>
	Remove only the /export partition from compute-0-0.
	</example>

	<example cmd='remove host partition compute-0-0 device=sdb1'>
	Remove only the partition information for /dev/sdb1 on compute-0-0
	</example>
	"""

	def run(self, params, args):
		if not len(args):
			self.abort('must supply host')
			
		(partition, device, uuid) = self.fillParams([
			('partition', None),
			('device', None),
			('uuid', None)])
			
		for host in self.getHostnames(args):
			conditions = []
			sql_cmd = """delete from partitions where
				node=(select id from nodes
				where name='%s')""" % host
			if uuid:
				conditions.append("uuid='%s'" % uuid)
			if partition:
				conditions.append("mountpoint='%s'" % partition)
			if device:
				conditions.append("device='%s'" % device)
			c = ' and '.join(conditions)
			if c:
				sql_cmd = "%s and %s" % (sql_cmd, c)

			self.db.execute(sql_cmd)

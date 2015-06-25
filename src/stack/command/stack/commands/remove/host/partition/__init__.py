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

import sys
import socket
import stack.commands
import string
from stack.exception import *

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
                        raise ArgRequired(self, 'host')
			
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

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
# Revision 1.4  2010/09/07 23:52:57  bruno
# star power for gb
#
# Revision 1.3  2010/04/14 14:40:26  bruno
# changed 'host bootaction' to 'bootaction' in the documentation portion of
# the commands
#
# Revision 1.2  2009/05/01 19:07:00  mjk
# chimi con queso
#
# Revision 1.1  2009/02/12 21:40:05  bruno
# make the bootaction global
#
#

import stack.commands
import stack.commands.set.bootaction
from stack.exception import *

import sys

class Command(stack.commands.HostArgumentProcessor,
	stack.commands.set.bootaction.command,
	stack.commands.remove.command):

	"""
	Remove a boot action specification from the system.

	<arg type='string' name='action'>
	The label name for the boot action. You can see the boot action label
	names by executing: 'stack list bootaction'.
	</arg>

	<param type='string' name='type'>
	The 'type' parameter should be either 'os' or 'install'.
	</param>

	<param type='string' name='os' optional="1">
	Specify the 'os' (e.g., 'redhat', 'sles', etc.)
	</param>

	<example cmd='remove bootaction action=default type=install'>
	Remove the default bootaction for installation.
	</example>
	"""

	def run(self, params, args):
		(b_action, b_type, b_os) = self.getBootActionTypeOS(params, args)
		if not self.actionExists(b_action, b_type, b_os):
			raise CommandError(self, 'action/type/os "%s/%s/%s" does not exists' % (b_action, b_type, b_os))

		self.db.execute("""delete from bootactions where
			os in (select id from oses where name = "%s") and
			bootname in (select id from bootnames where
			name = "%s" and type = "%s") """ %
			(b_os, b_action, b_type))


# @SI_Copyright@
#                             www.stacki.com
#                                  v1.0
# 
#      Copyright (c) 2006 - 2015 StackIQ Inc. All rights reserved.
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
# 	 "This product includes software developed by StackIQ" 
#  
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY STACKIQ AND CONTRIBUTORS ``AS IS''
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
# @SI_Copyright@

import os
import grp
import sys
import stack.commands
from stack.exception import *

class Command(stack.commands.set.command):
	"""
        Sets an Access control pattern.
        
	<param name="command" optional='0'>
	Command Pattern.
	</param>
        
	<param name="group" optional='0'>
	Group name / ID for access.
	</param>
        
	<example cmd='set access command="*" group=apache'>
	Give "apache" group access to all "stack" commands
	</example>
        
	<example cmd='set access command="list*" group=wheel'>
	Give "wheel" group access to all "stack list" commands
	</example>
	"""

	def run(self, params, args):

                
		(cmd, group) = self.fillParams([
                        ('command', None, True),
                        ('group',   None, True)
                        ])
                 
		groupid = None
		try:
			groupid = int(group)
		except ValueError:
			pass

		if groupid == None:
			try:
				groupid = grp.getgrnam(group).gr_gid
			except KeyError:
				raise CommandError(self, 'cannot find group %s' % group)

		if groupid == None:
			raise CommandError(self, 'cannot find group %s' % group)

                self.db.execute("""
                	insert into access (command, groupid)
                        values ('%s', %d)
                        """ % (cmd, groupid))

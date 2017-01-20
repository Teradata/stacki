#
# @SI_Copyright@
#                               stacki.com
#                                  v3.3
# 
#      Copyright (c) 2006 - 2017 StackIQ Inc. All rights reserved.
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
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL STACKIQ OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@
#

import sys
import stack.commands
from stack.commands.sync.host import Parallel
from stack.commands.sync.host import timeout


class Command(stack.commands.sync.host.command):
	"""
	Sync yum repo file to backend nodes.
	
	When a cart or pallet is added to the 
	frontend, to use the resulting repo but not
        reinstall machines, sync the new repo to the 
	backends for immediate use.

	<example cmd='sync host yum'>
	Giving no hostname or regex will sync
        to all backend nodes by default.
	</example>

	<example cmd='sync host yum backend-0-0'>
	Sync yum inventory file on backend-0-0
	</example>
	
	<example cmd='sync yum backend-0-[0-2]'>
	Using regex, sync yum inventory file on backend-0-0
	backend-0-1, and backend-0-2.
	</example>
	"""

	def run(self, params, args):
		sys.stdout = open('/dev/null')
		sys.stderr = open('/dev/null')

		hosts = self.getHostnames(args, managed_only=1)
		me = self.db.getHostname('localhost')

		threads = []
		for host in hosts:

                        attrs = {}
                        for row in self.call('list.host.attr', [ host ]):
                                attrs[row['attr']] = row['value']

			cmd = '/opt/stack/bin/stack report host yum %s | ' % host
			cmd += '/opt/stack/bin/stack report script | '

			if me != host:
				cmd += 'ssh -T -x %s ' % host
			cmd += 'bash > /dev/null 2>&1 '

			try:
				p = Parallel(cmd)
				p.start()
				threads.append(p)
			except:
				pass

		#
		# collect the threads
		#
		for thread in threads:
			thread.join(timeout)

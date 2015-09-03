# @SI_Copyright@
#                             www.stacki.com
#                                  v2.0
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
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL STACKIQ OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@

import string
import subprocess
import marshal

__stack__ = '/opt/stack/bin/stack'

rc = None

def ReturnCode():
	"""
	Get the return code of the previously run command.
	"""
	return rc


def Call(cmd, args=None, format='binary', sudo=False):
	"""
	Call the Stack Command Line and return a python dictionary as the
	result.  Currently only works with list commands.

	Example:
		result = stack.api.Call('list network', [ 'private' ])
	"""

	global rc
	
	command = cmd.replace('.', ' ').strip().split()
	
	if sudo:
		list = [ sudo ]
	else:
		list = [ ]
	list.append(__stack__)
	list.extend(command)
	if args:
		list.extend(args)

	if command[0] == 'list':
		list.append('output-format=%s' % format)
	
	s = None
	p = subprocess.Popen(list, stdout=subprocess.PIPE)
	for line in p.stdout.readlines():
		if not s:
			s = line
		else:
			s += line
	rc = p.wait()
	if rc:
		return [ ]

	if command[0] == 'list':
		if s:
			return marshal.loads(s)
		return [ ]
	
	if s:
		return s.split('\n')
	return [ ]



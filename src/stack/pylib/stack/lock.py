# @SI_Copyright@
#                             www.stacki.com
#                                  v3.1
# 
#      Copyright (c) 2006 - 2016 StackIQ Inc. All rights reserved.
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

import os
import fcntl

class Semaphore:
	"""
	Used to manage a on disk semaphore. No locking
	is provided.
	"""

	def __init__(self, path):
		self.path = path

	def read(self):
		try:
			fin = open(self.path, 'r')
		except:
			return None
		try:
			count = int(fin.read())
			fin.close()
		except:
			return None
		return count

	def write(self, count):
		try:
			fout = open(self.path, 'w')
		except:
			return None

		fout.write('%d' % count)
		fout.close()


class Mutex:
	"""
	Used the acquire and release a on disk mutex
	"""
     
	def __init__(self, path):
		self.path = path
		self.file = open(path, 'w')

	def __del__(self):
		self.release()
		self.file.close()
    
	def acquire(self):
		fcntl.flock(self.file, fcntl.LOCK_EX)

	def acquire_nonblocking(self):
		retval = 0
		try:
			fcntl.flock(self.file, fcntl.LOCK_EX | fcntl.LOCK_NB)
		except:
			retval = 1

		return retval
        
	def release(self):
		fcntl.flock(self.file, fcntl.LOCK_UN)
       

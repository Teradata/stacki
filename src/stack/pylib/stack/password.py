#! /opt/stack/bin/python
# @SI_Copyright@
#                               stacki.com
#                                  v4.0
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

import os
import sys
import base64
import crypt
import random
import time


class Password:
	def __init__(self):
		s = long(time.time()*pow(10, 9))
		random.seed(s)

	def get_rand(self, num_bytes=16):
		c = ''
		for i in range(num_bytes):
			c = c + chr(random.getrandbits(8))
			random.seed(long(time.time()*pow(10, 9)))
		return c

	def get_salt(self):
		salt = '$1$'
		s = self.get_rand()
		salt = salt + base64.urlsafe_b64encode(s)[0:8]
		return salt

	def get_cleartext_pw(self, c_pw = None):
		if not c_pw:
			c = self.get_rand()
			c_pw = base64.urlsafe_b64encode(c)
			c_pw = c_pw.rstrip('=')
		return c_pw

	def get_crypt_pw(self, c_pw = None):
		# if c_pw was not specified, generate a random password
		if not c_pw:
			c_pw = self.get_cleartext_pw()
		salt = self.get_salt()
		return crypt.crypt(c_pw, salt)

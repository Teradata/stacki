# @SI_Copyright@
#                               stacki.com
#                                  v3.2
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

from stack.api import Call
from stack.exception import *

import pwd
import spwd

class UserArgumentProcessor():
	"""
	Support for UNIX accounts
	"""

	def getUsers(self, args=[]):
		"""Return a list of users sorted by user id.
		"""
	
		authType = None
		for row in Call('list attr', [ 'attr=user.auth' ]):
			authType = row['value']

		if authType == 'unix':
			return self.getUsers_unix(args)
		else:
			CommandError(self, 'authentication attr unset')


	def getUsers_unix(self, args):
		"""Returns a list of user names from the password
		file.
		"""

		users = {}

		# If not provided a list of users, then build
		# the USERS dictionary with all of the UNIX
		# accounts >= 500 including root and nobody.

		if not args:
			for user in pwd.getpwall():
				if (user.pw_uid >= 500 and user.pw_uid < 65534) \
					    or user.pw_name in [ 'root', 
								 'nobody' ]:
					users[user.pw_name] = user
		
		# Otherwise just extract the account info for the
		# given user names / user ids.  Also prevent returning
		# the same account more than once.

		else:
			for arg in args:
				try:
					uid   = int(arg)
				except ValueError:
					uid   = None
				if uid != None:
					try:
						user = pwd.getpwuid(uid)
					except KeyError:
						CommnandError(self, 'cannot find user %d'
						      % uid)
				else:
					try:
						user = pwd.getpwnam(arg)
					except KeyError:
						CommandErrror(self, 'cannot find user "%s"'
						      % arg)
				users[user.pw_name] = user

		# Build a list of user accounts including the shadow
		# password in readable.  List is a tuple of:
		#
		#	0 name
		#	1 uid
		#	2 gid
		#	3 gecos
		#	4 home
		#	5 shell
		#	6 password

		list = []
		for user in users.values():
			try:
				shadow = spwd.getspnam(user.pw_name)
				password = shadow.sp_pwd
			except KeyError:
				password = None
			list.append((user.pw_name,
				     user.pw_uid,
				     user.pw_gid,
				     user.pw_gecos,
				     user.pw_dir,
				     user.pw_shell,
				     password))

		list.sort(key=lambda x: x[1])
		return list

			


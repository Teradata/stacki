# @SI_Copyright@
#				stacki.com
#				   v3.3
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
#	 "This product includes software developed by StackIQ" 
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
import stack
import stack.commands
from stack.exception import CommandError


class Implementation(stack.commands.Implementation):
	"""
	Copy SLES Stacki Pallet
	"""
	
	def run(self, args):

		(clean, prefix, info) = args

		name = info.getRollName()
		vers = info.getRollVersion()
		arch = info.getRollArch()
		release = info.getRollRelease()
		OS = info.getRollOS()

		roll_dir = os.path.join(prefix, name)
		new_roll_dir = os.path.join(roll_dir, vers, release, OS, arch)

		#
		# Clean out the existing roll directory if asked
		#
		if clean and os.path.exists(new_roll_dir):
			print('Cleaning %s %s-%s' % (name, vers, release), end=' ')
			print('for %s from the pallets directory' % arch)

			if os.path.exists(new_roll_dir):
				os.system('/bin/rm -rf %s' % new_roll_dir)

		#
		# copy the roll to the HD
		#
		sys.stdout.write('Copying %s %s-%s to pallets ...' %
			(name, vers, release))
		sys.stdout.flush()

		os.chdir(os.path.join(self.owner.mountPoint, name))

		new_format = os.path.join(vers, release, OS, arch)
		if os.path.exists(new_format):
			os.chdir(new_format)
		else:
			raise CommandError(self.owner, 'unrecognized pallet format')

		os.system('find . ! -name TRANS.TBL -print | cpio -mpud %s'
			% new_roll_dir)

		#
		# go back to the top of the pallet
		#
		os.chdir(os.path.join(self.owner.mountPoint, name))


		# after copying the roll, make sure everyone (apache included)
		# can traverse the directories

		os.system('find %s -type d -exec chmod a+rx {} \;' % roll_dir)


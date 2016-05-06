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


import re
import sys
import stack.csv
import stack.commands
from stack.exception import *

class Implementation(stack.commands.ApplianceArgumentProcessor,
	stack.commands.HostArgumentProcessor, stack.commands.Implementation):	

	"""
	Unload (remove) hosts from the database based on comma-separated
	formatted file.
	"""

	def run(self, args):
		filename, = args

		hosts = self.getHostnames()

		reader = stack.csv.reader(open(filename, 'rU'))
		header = None
                dict   = {}
		for row in reader:
			if not header:
				header = row

				#
				# make checking the header easier
				#
				required = [ 'name' ] 

				for i in range(0, len(row)):
					if header[i] in required:
						required.remove(header[i])

				if len(required) > 0:
                                        raise CommandError(self.owner, 'csv file is missing column(s) "%s"' % ', '.join(required))

				continue

			for i in range(0, len(row)):
				field = row[i]

				if header[i] == 'name' and field in hosts:
                                        dict[field] = True


                for host in dict.keys():
			self.owner.call('remove.host', [ host ])
		self.owner.call('sync.config')
		self.owner.call('sync.host.config')


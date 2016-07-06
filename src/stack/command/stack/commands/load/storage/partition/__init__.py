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
import os
import os.path
import sys
import shutil
import stack.commands
from stack.exception import *

class Command(stack.commands.load.command,
               stack.commands.HostArgumentProcessor):
	"""
	Take rows from a spreadsheet that describe how a host's disk partitions
	should be configured and then place those values into the database.
	
	<param type='string' name='file'>
	The file that contains the storage disk partition configuration.
	</param>

	<param type='string' name='processor' optional='1'>
	The processor used to parse the file.
	Default: default.
	</param>
	
	<example cmd='load storage partition file=partitions.csv'>
	Read disk partition configuration from partitions.csv and use the
	default processor to parse the data.
	</example>
	"""		

	def run(self, params, args):
                filename, processor = self.fillParams([ 
			('file', None, True),
			('processor', 'default') 
			])

		if not filename:
			raise ParamValue(self, 'file', 'valid csv filename')
		if not os.path.exists(filename):
			raise CommandError(self, 'file "%s" does not exist' % filename)	

		#
		# implementations can't return values
		#
		self.hosts = {}
		self.runImplementation('load_%s' % processor, (filename, ))

		args = self.hosts
		self.runPlugins(args)

		#
		# checkin the spreadsheet
		#
		sheetsdir = '/export/stack/spreadsheets'
		if not os.path.exists(sheetsdir):
			os.makedirs(sheetsdir)
			
		RCSdir = '%s/RCS' % sheetsdir
		if not os.path.exists(RCSdir):
			os.makedirs(RCSdir)

		sheetsfile = '%s/%s' % (sheetsdir, os.path.basename(filename))
		if not os.path.exists(sheetsfile) or not \
			os.path.samefile(filename, sheetsfile):
			shutil.copyfile(filename, '%s' % sheetsfile)
		
		cmd = 'date | /opt/stack/bin/ci "%s"' % sheetsfile
		os.system(cmd)

		cmd = '/opt/stack/bin/co -f -l "%s"' % sheetsfile
		os.system(cmd)


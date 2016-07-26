# @SI_Copyright@
#                               stacki.com
#                                  v3.3
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

from __future__ import print_function
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
	Load attributes into the database
	
	<param type='string' name='file' optional='1'>
	The file that contains the attribute data to be loaded into the
	database.
	</param>

	<param type='string' name='processor'>
	The processor used to parse the file and to load the data into the
	database. Default: default.
	</param>
	
	<example cmd='load attrfile file=attrs.csv'>
	Load all the attributes in file named attrs.csv and use the default
	processor.
	</example>
	
	<related>unload attrfile</related>
	"""		

	def checkValue(self, value):
		#
		# make sure the value:
		#
		#	0) is on a single line
		for c in value:
			if c in [ '\n' ]:
				raise CommandError(self, 'value "%s" cannot be multi-line' % value)

	def checkAttr(self, attr):
		#
		# make sure the attribute:
		#
		#	0) isn't 'target'
		#	1) has only zero or one '/'
		#	2) is a ctoken
		#
		if attr.lower() == 'target':
			return

		if ' ' in attr:
                        raise CommandError(self, 'attribute "%s" cannot have a space character' % attr)

		a = attr.split('/')
		if len(a) > 2:
                        raise CommandError(self, 'attribute "%s" cannot have more than one "/"' % attr)

		ctoken = '[A-Za-z_][A-Za-z0-9_]*$'
		for t in a:
			for token in t.split('.'):
				if not re.match(ctoken, token):
					raise CommandError(self, 'attribute "%s" contains an invalid character.\n"%s" must be a valid ctoken' % (attr, token))

		return
			

	def run(self, params, args):
                filename, processor = self.fillParams([
                        ('file', None, True),
			('processor', 'default')
                        ])

		if not os.path.exists(filename):
                        raise CommandError(self, 'file "%s" does not exist' % filename)

		#
		# implementations can't return values
		#
		self.attrs = {}
		self.runImplementation('load_%s' % processor, (filename, ))

		self.runPlugins(self.attrs)

		self.command('sync.config')

                # Only sync the host config for the hosts in the
                # imported spreadsheet.

                hosts = self.getHostnames()
                for host in self.attrs.keys():
                        if host in hosts:
                                self.call('sync.host.config', [ host ])
        

		#
		# checkin the attribute spreadsheet
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


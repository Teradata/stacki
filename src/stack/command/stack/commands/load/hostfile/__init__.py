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
# @Copyright@
#  				Rocks(r)
#  		         www.rocksclusters.org
#  		         version 5.4 (Maverick)
#  
# Copyright (c) 2000 - 2010 The Regents of the University of California.
# All rights reserved.	
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
# 	"This product includes software developed by the Rocks(r)
# 	Cluster Group at the San Diego Supercomputer Center at the
# 	University of California, San Diego and its contributors."
# 
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.  The name of the
# software includes the following terms, and any derivatives thereof:
# "Rocks", "Rocks Clusters", and "Avalanche Installer".  For licensing of 
# the associated name, interested parties should contact Technology 
# Transfer & Intellectual Property Services, University of California, 
# San Diego, 9500 Gilman Drive, Mail Code 0910, La Jolla, CA 92093-0910, 
# Ph: (858) 534-5815, FAX: (858) 534-7345, E-MAIL:invent@ucsd.edu
#  
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS''
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
# @Copyright@


import shutil
import os.path
import stack.commands
from stack.exception import *

class Command(stack.commands.load.command):
	"""
	Load host info into the database.
	
	<param type='string' name='file'>
	The file that contains the host data to be loaded into the
	database.
	</param>

	<param type='string' name='processor'>
	The processor used to parse the file and to load the data into the
	database. Default: default.
	</param>
	
	<example cmd='load hostfile file=hosts.csv'>
	Load all the host info in file named hosts.csv and use the default
	processor.
	</example>
	
	<related>unload hostfile</related>
	"""		

	def doGoogle(self, filename):
		import gspread
		import csv
		import getpass

		username = raw_input(
			'Enter your Google account name: ')
		password = getpass.getpass(
			'Enter your Google account password: ')

		gc = gspread.login(username, password)
		worksheet = gc.open(filename).sheet1
		reader = worksheet.get_all_values()
			
		filename = '/tmp/%s.csv' % filename
		file = open(filename, 'w')
		writer = csv.writer(file)

		for row in reader:
			writer.writerow(row)

		file.close()
	
		return filename


	def run(self, params, args):
                filename, processor = self.fillParams([
                        ('file', None),
			('processor', 'default')
                        ])

                googleacct = self.str2bool(self.getAttr('google.credential'))
                if googleacct:
			#
			# this may be a Google spreadsheet
			#
			googlefile = self.doGoogle(filename)
			if not googlefile:
                                raise CommandError(self, 'file "%s" does not exist' % filename)
			filename = googlefile
                else:
                	if not file:
                        	raise ParamRequired(self, 'file')

                        if not os.path.exists(filename):
                                raise CommandError(self, 'file "%s" does not exist' % filename)

		self.hosts = {}
		self.interfaces = {}
		self.runImplementation('load_%s' % processor, (filename, ))

		args = self.hosts, self.interfaces
		self.runPlugins(args)

                # Set each host's default boot action to os, before we
                # build out the DHCP file with sync.config

                params = []
                for host in self.hosts.keys():
                        params.append(host)
                params.append('action=os')
		self.call('set.host.boot', params)
                
		self.call('sync.config')

                self.call('sync.host.config', self.hosts.keys())
		
		#
		# checkin the hosts spreadsheet
		#
		sheetsdir = '/export/stack/spreadsheets'
		if not os.path.exists(sheetsdir):
			os.makedirs(sheetsdir)
			
		RCSdir = '%s/RCS' % sheetsdir
		if not os.path.exists(RCSdir):
			os.makedirs(RCSdir)

		#
		# if the 'sheetsfile' doesn't exist or if the 'sheetsfile' and
		# the 'filename' are not the same file, then copy 'filename'
		# to 'sheetsfile'.
		#
		sheetsfile = '%s/%s' % (sheetsdir, os.path.basename(filename))
		if not os.path.exists(sheetsfile) or not \
				os.path.samefile(filename, sheetsfile):
			shutil.copyfile(filename, '%s' % sheetsfile)

		cmd = 'date | /opt/stack/bin/ci "%s"' % sheetsfile
		os.system(cmd)

		cmd = '/opt/stack/bin/co -f -l "%s"' % sheetsfile
		os.system(cmd)


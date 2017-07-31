# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@

import sys
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


	def run(self, params, args):
		filename, processor = self.fillParams([
			('file', None),
			('processor', 'default')
			])

		if not file:
			raise ParamRequired(self, 'file')

		if not os.path.exists(filename):
			raise CommandError(self, 'file "%s" does not exist' % filename)

		self.hosts = {}
		self.interfaces = {}

		sys.stderr.write('Loading Spreadsheet\n')
		self.runImplementation('load_%s' % processor, (filename, ))

		sys.stderr.write('Configuring Database\n')
		args = self.hosts, self.interfaces
		self.runPlugins(args)

		# Set each host's default boot action to os, before we
		# build out the DHCP file with sync.config

		sys.stderr.write('Setting Bootaction to OS\n')
		argv = self.hosts.keys()
		argv.append('action=os')
		argv.append('sync=false')
		self.call('set.host.boot', argv)
		
		self.call('sync.config')

		argv = self.hosts.keys()
		self.call('sync.host.config', argv)
		
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


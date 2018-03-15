# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import sys
import shutil
import os.path
import stack.commands
from stack.exception import ParamRequired, CommandError


class Command(stack.commands.load.command,
	      stack.commands.SwitchArgumentProcessor):
	"""
	Load switch info into the database.
	
	<param type='string' name='file'>
	The file that contains the switch data to be loaded into the
	database.
	</param>

	<param type='string' name='processor'>
	The processor used to parse the file and to load the data into the
	database. Default: default.
	</param>
	
	<example cmd='load switchfile file=hosts.csv'>
	Load all the switch info in file named hosts.csv and use the default
	processor.
	</example>
	"""		


	def run(self, params, args):
		filename, processor = self.fillParams([
			('file', None),
			('processor', 'default')
			])

		if not filename:
			raise ParamRequired(self, 'file')

		if not os.path.exists(filename):
			raise CommandError(self, 'file "%s" does not exist' % filename)

		self.switches= {}

		sys.stderr.write('Loading Spreadsheet\n')
		self.runImplementation('load_%s' % processor, (filename, ))

		sys.stderr.write('Configuring Database\n')
		args = self.switches
		self.runPlugins(args)

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
		if not os.path.exists(sheetsfile) or not os.path.samefile(filename, sheetsfile):
			shutil.copyfile(filename, '%s' % sheetsfile)

		cmd = 'date | /opt/stack/bin/ci "%s"' % sheetsfile
		os.system(cmd)

		cmd = '/opt/stack/bin/co -f -l "%s"' % sheetsfile
		os.system(cmd)


# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#


import os
import os.path
import shutil

import stack.commands
from stack.commands import NetworkArgProcessor
from stack.exception import CommandError


class Command(NetworkArgProcessor, stack.commands.load.command):
	"""
	Take rows from a spreadsheet that describe the logical networks that
	should be configured and then place those values into the database.
	
	<param type='string' name='file'>
	The file that contains the logical network configuration.
	</param>

	<param type='string' name='processor' optional='1'>
	The processor used to parse the file.
	Default: default.
	</param>
	
	<example cmd='load networkfile file=mynets.csv'>
	Read network configuration from mynets.csv and use the
	default processor to parse the data.
	</example>

	<related>report networkfile</related>
	<related>load</related>
	<related>dump network</related>
	"""		

	def run(self, params, args):
		filename, processor = self.fillParams([
			('file', None, True),
			('processor', 'default') ])

		if not os.path.exists(filename):
			raise CommandError(self, 'file "%s" does not exist' % filename)

		#
		# implementations can't return values
		#
		self.networks = {}
		self.columns = {}
		self.runImplementation('load_%s' % processor, (filename, ))
		args = self.networks, self.current_networks
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


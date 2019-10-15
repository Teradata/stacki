# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os
import os.path
import shutil
import stack.commands
from stack.exception import CommandError


class Command(stack.commands.load.command, stack.commands.HostArgumentProcessor):
	"""
	Take rows from a spreadsheet that describe how a host's disk partitions
	should be configured and then place those values into the database.

	<param type='string' name='file' optional='0'>
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

		if not os.path.exists(filename):
			raise CommandError(self, 'file "%s" does not exist' % filename)

		# Implementations can't return values
		self.hosts = {}
		self.runImplementation('load_%s' % processor, (filename, ))

		self.runPlugins(self.hosts)

		# Check-in the spreadsheet
		sheetsdir = '/export/stack/spreadsheets'
		if not os.path.exists(sheetsdir):
			os.makedirs(sheetsdir)

		RCSdir = '%s/RCS' % sheetsdir
		if not os.path.exists(RCSdir):
			os.makedirs(RCSdir)

		sheetsfile = '%s/%s' % (sheetsdir, os.path.basename(filename))
		if not os.path.exists(sheetsfile) or not os.path.samefile(filename, sheetsfile):
			shutil.copyfile(filename, '%s' % sheetsfile)

		os.system('date | /opt/stack/bin/ci "%s"' % sheetsfile)

		os.system('/opt/stack/bin/co -f -l "%s"' % sheetsfile)

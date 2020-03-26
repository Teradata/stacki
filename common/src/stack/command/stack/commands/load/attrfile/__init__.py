# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import re
import os
import os.path
import shutil

import stack.commands
from stack.commands import HostArgProcessor
from stack.exception import CommandError


class Command(HostArgProcessor, stack.commands.load.command):
	"""
	Load attributes into the database. The attribute csv file needs to have a mandatory 'target'
	column with hostnames. There are 2 ways of specifying attribute name, value:
	1. Add 'attrName', 'attrVal' columns  with attribute name and value respectively.
	2. The attribute name can also be a column in the spreadsheet and the cell at the
	intersection of a hostname row can contain the attribute value.

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

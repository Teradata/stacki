# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

import os.path
import stack.commands
from stack.exception import *

class Command(stack.commands.unload.command):
	"""
	Unload (remove) attributes from the database
	
	<param type='string' name='file' optional='0'>
	The file that contains the attribute data to be removed from the
	database.
	</param>

	<param type='string' name='processor'>
	The processor used to parse the file and to remove the data into the
	database. Default: default.
	</param>
	
	<example cmd='unload attrfile file=attrs.csv'>
	Remove all the attributes in file named attrs.csv and use the default
	processor.
	</example>
	
	<related>load attrfile</related>
	"""		

	def run(self, params, args):
		filename, processor = self.fillParams([
			('file', None, True),
			('processor', 'default')
			])

		if not os.path.exists(filename):
			raise CommandError(self, 'file "%s" does not exist' % filename)

		self.attrs = {}
		self.runImplementation('unload_%s' % processor, (filename, ))

		self.runPlugins(self.attrs)


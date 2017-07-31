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
	Unload (remove) hosts from the database
	
	<param type='string' name='file' optional='0'>
	The file that contains the host data to be removed from the database.
	</param>

	<param type='string' name='processor'>
	The processor used to parse the file and to remove the data into the
	database. Default: default.
	</param>
	
	<example cmd='unload hostfile file=hosts.csv'>
	Remove all the hosts in file named hosts.csv and use the default
	processor.
	</example>
	
	<related>load hostfile</related>
	"""		

	def run(self, params, args):
		filename, processor = self.fillParams([
			('file', None, True),
			('processor', 'default')
			])

		if not os.path.exists(filename):
			raise CommandError(self, 'file "%s" does not exist' % filename)

		self.runImplementation('unload_%s' % processor, (filename, ))


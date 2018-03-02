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


import stack.commands
from stack.exception import CommandError


class command(stack.commands.Command):
	MustBeRoot = 0

	safe_chars = [
		'@', '%', '^', '-', '_', '=', '+', 
		':', 
		',', '.', '/'
		]
		
	def quote(self, s):
		retval = ''

		if s is not None:
			try:
				for c in str(s):
					if c.isalnum() or c in self.safe_chars:
						retval += c
					else:
						retval += '\\%s' % c
			except:
				pass
		return retval

	def dump(self, line):
		self.addText('/opt/stack/bin/stack %s\n' % line)
#		self.addText('./stack.py %s\n' % line)

	
class Command(command):
	"""
	The top level dump command is used to recursively call all the
	dump commands in the correct order.  This is used to create the 
	restore roll.

	<example cmd='dump'>
	Recursively call all dump commands.
	</example>
	"""
	
	def run(self, params, args):
		if len(args):
			raise CommandError(self, 'command does not take arguments')
		self.addText("#!/bin/bash\n\n")
		self.runPlugins()
		self.dump("sync config")
		self.dump("sync host config")


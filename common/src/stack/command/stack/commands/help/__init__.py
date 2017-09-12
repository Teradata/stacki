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


import string
import stack.commands


class command(stack.commands.Command):

	MustBeRoot = 0

	
class Command(command):
	"""
	List help for the command line client.  With no arguments it lists
	all the commands available.  Otherwise it will list the subset
	of command with the specified string (see examples).

	<arg type='string' name='command'>
	The substring matched against all commands.
	</arg>

	<example cmd='help'>
	Alias for 'rocks list help'
	</example>

	<example cmd='help viz'>
	Lists all the commands with the string 'viz' in the name.
	</example>

	<example cmd='help list host'>
	Lists all the commands with the string 'list host' in the name.
	</example>
	"""

	def run(self, params, args):

		help = self.command('list.help', [ 'cols=0' ])
		sub  = ''.join(args)

		if not args:
			self.addText(help)
		else:
			for line in help.split('\n'):
				if line:
					if string.find(line, sub) >= 0:
						self.addText('%s\n' % line)
		

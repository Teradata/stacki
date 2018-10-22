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
	Lists all the available commands.
	</example>

	<example cmd='help viz'>
	Lists all the commands with the string 'viz' in the name.
	</example>

	<example cmd='help list host'>
	Lists all the commands with the string 'list host' in the name.
	</example>
	"""

	def run(self, params, args):
		command_list = self.command('list.help', [ 'cols=0' ])
		substring = ' '.join(args)

		if not args:
			self.addText(command_list)
		else:
			for line in command_list.split('\n'):
				if line and substring in line:
					self.addText('%s\n' % line)

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


import os
import stack.file
import stack.commands
from stack.exception import CommandError


class Command(stack.commands.list.command):
	"""The Help Command print the usage of all the registered
	Commands.

	<param optional='1' type='string' name='subdir'>
	Relative of Python commands for listing help.  This is used internally
	only.
	</param>

	<example cmd='list help'>
	List help for all commands
	</example>

	<example cmd='list help subdir=list/host'>
	List help for all commands under list/host
	</example>
	"""

	def run(self, params, args):

		# Because this command is called directly from the stack.py
		# code we need to provide the params argument.  This is the
		# only command where we need to include this argument.

		(subdir, cols) = self.fillParams([
			('subdir', ),
			('cols', '80')
			], params)

		try:
			cols = int(cols)
		except:
			cols = 80

		if subdir:
			filepath = os.path.join(stack.commands.__path__[0],
				subdir)
			modpath  = 'stack.commands.%s' % '.'.join(subdir.split(os.sep))
		else:
			filepath = stack.commands.__path__[0]
			modpath  = 'stack.commands'

		tree = stack.file.Tree(filepath)
		paths = sorted(tree.getDirs())

		for path in paths:
			# ignore python3 cache files
			if not path or '__pycache__' in path:
				continue

			module = '%s.%s' % (modpath, '.'.join(path.split(os.sep)))
			# ignore unix hidden files, too
			if '..' in module:
				continue

			try:
				__import__(module)
			except ImportError:
				raise CommandError(self, '%s import failed (missing or bad file)' % module)
			module = eval(module)

			try:
				o = getattr(module, 'Command')(None)
			except AttributeError:
				continue

			# Format the brief usage to fit within the
			# width of the user's window (default to 80 cols)

			cmd = ' '.join(path.split(os.sep))
			l   = len(cmd) + 1
			s   = ''
			for arg in o.usage().split():
				if l + len(arg) < cols or cols == 0:
					s += '%s ' % arg
					l += len(arg) + 1 # space
				else:
					s += '\n\t%s ' % arg
					l  = len(arg) + 9 # tab + space

			self.addText('%s %s\n' % (cmd, s))



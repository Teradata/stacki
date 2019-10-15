# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import stack.commands
from stack.exception import CommandError
import shutil
from collections import namedtuple
from pytest import main
from glob import glob
import os


class Command(stack.commands.Command,
	stack.commands.HostArgumentProcessor):
	"""
	<arg type='string' name='options' repeat='1'>
	Zero or more options to pass to pytest.
	</arg>

	<param type='boolean' name='exitonfail' optional='0'>
	Will exit on the first failure. Then
	you have the chance to fix it and try
	again.

	Maybe we'll give you advice on how to fix it. Maybe
	we won't. Depends on our mood.

	Otherwise run all tests.

	Default is false and all tests are run.
	</param>

	<param type='boolean' name='pretty' optional='0'>
	If you really, really want to see the tracebacks and confuse
	the hell out of yourself, set this to False.

	Otherwise it is true by default, so it will be pretty.

	For you.
	</param>

	Test cases for basic stacki support needs.

	"""

	def run(self, params, args):
		(exitonfail, pretty) = self.fillParams([
			('exitonfail', False),
			('pretty', True)
			])

		exitonfail = self.str2bool(exitonfail)
		pretty = self.str2bool(pretty)

		current_dir = os.getcwd()
		os.chdir('/opt/stack/lib/python3.7/site-packages/stack/commands/report/system')
		tests = glob('tests/*')

		# make it real ugly.
		# Pytest -rs option is used to output message when a test is skipped
		if exitonfail and not pretty:
			_return_code = main(['--verbose', '--exitfirst', '-rs', *args, *tests])
		# exit with first failure
		elif exitonfail:
			_return_code = main(['--verbose', '--capture=no', '--exitfirst', '-rs', *args, *tests])
		# show tracebacks of failures but don't fail.
		elif not pretty:
			_return_code = main(['--verbose', '--capture=no', '-rs', *args, *tests])
		# pretty and no tracebacks
		else:
			_return_code = main(['--verbose', '--capture=no', '--tb=no', '-rs', *args, *tests])

		os.chdir(current_dir)

		# If any of the tests failed, throw an error
		if _return_code > 0:
			raise CommandError(self, "One or more tests failed")

# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import stack.commands
import shutil
from collections import namedtuple
from pytest import main
from glob import glob
import os

class Command(stack.commands.Command,
	stack.commands.HostArgumentProcessor):
	"""
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
		os.chdir('/opt/stack/lib/python3.6/site-packages/stack/commands/report/system')
		tests = glob('tests/*')

		# make it real ugly.
		if exitonfail == True and pretty == False:
			main(['-v', '-x', *tests])
		# exit with first failure
		if exitonfail == True:
			main(['-v', '-s', '-x', *tests])
		# show tracebacks of failures but don't fail.
		elif pretty == False:
			main(['-v', '-s', *tests])
		# pretty and no tracebacks
		else:
			main(['-v', '-s', '--tb=no', *tests])

		os.chdir(current_dir)

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
	Test cases for basic stacki needs
	"""

	def run(self, params, args):
		current_dir = os.getcwd()
		os.chdir('/opt/stack/lib/python3.6/site-packages/stack/commands/report/system')
		tests = glob('tests/*')
		main(['-x', '-v', *tests])
		os.chdir(current_dir)
	

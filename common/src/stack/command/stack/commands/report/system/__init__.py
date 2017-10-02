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



class Command(stack.commands.Command,
	stack.commands.HostArgumentProcessor):
	"""
	Test cases for basic stacki needs
	"""

	def run(self, params, args):
		tests = glob('tests/*')
		main(['-x', '-v', *tests])

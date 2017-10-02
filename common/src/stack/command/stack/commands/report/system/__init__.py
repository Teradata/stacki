# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import stack.commands
import shutil

def test_dir(path):
	total, used, free = shutil.disk_usage(path)
	result = ["",""]
	result[0] = "Check if `%s` is not full" % path
	try:
		assert free > 0
		result[1] = "[ Passed ]"
	except:
		result[1] = "[ Failed ]"

	return result

class Command(stack.commands.Command,
	stack.commands.HostArgumentProcessor):
	"""
	Test cases for basic stacki needs
	"""

	def run(self, params, args):

		test_results = []

		for path in ['/', '/var', '/export']:
			test_results.append(test_dir(path))

		self.beginOutput()
		for result in test_results:
			self.addOutput("", result)
		self.endOutput(header=["","Test", "Result"])

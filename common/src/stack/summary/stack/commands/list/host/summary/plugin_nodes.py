#
# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import stack.commands

class Plugin(stack.commands.Plugin):
	def provides(self):
		return "nodes"

	def requires(self):
		return []

	def run(self, params):
		self.owner.addOutput('localhost',
			('Host Count',
			len(self.owner.hosts)))

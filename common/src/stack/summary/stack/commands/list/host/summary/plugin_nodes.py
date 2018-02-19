#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
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

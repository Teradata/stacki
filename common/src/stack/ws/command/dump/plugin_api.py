# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'api'

	def run(self, args):
		return self.owner.command('dump.api')


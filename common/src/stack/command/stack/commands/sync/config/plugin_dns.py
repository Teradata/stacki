# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
#

import stack.commands


class Plugin(stack.commands.Plugin):
	"Writes DNS configuration"

	def provides(self):
		return 'dns'

	def run(self, args):
		self.owner.command('sync.dns', [])


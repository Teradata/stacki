# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

import stack.commands

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'repo'
		
	def run(self, args):
		self.owner.command('sync.host.repo', [ 'localhost' ])


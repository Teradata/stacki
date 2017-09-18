# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Command(stack.commands.sync.host.command):

	def run(self, params, args):

		self.notify('Sync Host Boot\n')

		argv = self.getHostnames(args, managed_only=True)
		argv.append('notify=true')
		self.report('report.host.bootfile', argv)

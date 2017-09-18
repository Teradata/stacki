# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Implementation(stack.commands.Implementation):

	def run(self, args):
		host = args[0]

		self.owner.addOutput(host, '<stack:file stack:name="/etc/resolv.conf">')
		self.owner.outputResolv(host)
		self.owner.addOutput(host, '</stack:file>')


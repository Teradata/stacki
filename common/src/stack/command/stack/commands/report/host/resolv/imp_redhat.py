# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Implementation(stack.commands.Implementation):

	def run(self, args):
		host = args[0]

		self.owner.addOutput(host, '<stack:file stack:name="/etc/resolv.conf">')
		self.owner.outputResolv(host)
		self.owner.addOutput(host, '</stack:file>')


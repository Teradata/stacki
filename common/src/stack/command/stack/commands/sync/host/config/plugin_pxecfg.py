#
# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
#

import stack.commands


class Plugin(stack.commands.Plugin):
	"Sets the hosts' bootaction to install"

	def provides(self):
		return 'pxeconfig'

	def requires(self):
		return []

	def run(self, h):
		hosts = h['hosts']
		attrs = h['attrs']

		self.owner.command('sync.host.boot', hosts)

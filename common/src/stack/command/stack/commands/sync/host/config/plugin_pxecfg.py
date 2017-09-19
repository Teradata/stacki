#
# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
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

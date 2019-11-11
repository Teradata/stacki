# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
#

import stack.commands


class Plugin(stack.commands.Plugin):
	"re-write and sync ntp config on the frontend"

	def provides(self):
		return 'time'

	def requires(self):
		return ['dhcpd']

	def run(self, args):
		self.owner.command('sync.host.time', ['localhost'])

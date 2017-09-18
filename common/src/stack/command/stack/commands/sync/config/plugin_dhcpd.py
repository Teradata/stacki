# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
#

import stack.commands


class Plugin(stack.commands.Plugin):
	"Writes /etc/dhcpd.conf"

	def provides(self):
		return 'dhcpd'

	def requires(self):
		return ['hostfile']

	def run(self, args):
		self.owner.command('sync.dhcpd')

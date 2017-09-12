# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'group'

	def run(self, hosts):
		for host in hosts:
			self.owner.db.execute("""delete from memberships
				where nodeid = (select id from nodes where name = '%s') """ %
				(host))

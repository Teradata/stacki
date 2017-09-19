# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'group'

	def run(self, hosts):
		for host in hosts:
			self.owner.db.execute("""delete from memberships
				where nodeid = (select id from nodes where name = '%s') """ %
				(host))

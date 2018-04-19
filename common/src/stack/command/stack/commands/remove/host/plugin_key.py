# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'key'

	def run(self, hosts):
		for host in hosts:
			self.owner.db.execute("""delete from public_keys where
				node = (select id from host_view where name = '%s') """ %
				(host))

# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'firewall'

	def run(self, hosts):
		#
		# since we are not setting any command line parameters, we
		# just need to remove all rows in the database that match this
		# host
		#
		for host in hosts:
			self.db.execute("""delete from node_firewall where
				node = (select id from host_view where
				name = '%s')""" % host)	


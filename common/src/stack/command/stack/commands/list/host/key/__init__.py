# @copyright@
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@


import stack.commands


class Command(stack.commands.list.host.command):
	"""
	List the public keys for hosts.
	
	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied,
	information for all hosts will be listed.
	</arg>
	"""

	def run(self, params, args):
		self.beginOutput()

		for host in self.getHostnames(args):
			self.db.execute("""select id, public_key from
				public_keys where node = (select id from
				host_view where name = '%s') """ % host)
		
			for id, key in self.db.fetchall():
				i = 0	
				for line in key.split('\n'):
					if i == 0:
						self.addOutput(host, (id, line))
					else:
						self.addOutput('', (' ', line))
					i += 1

		self.endOutput(header=['host', 'id', 'public key'],
			trimOwner=False)


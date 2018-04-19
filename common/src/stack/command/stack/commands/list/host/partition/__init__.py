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
	Lists the partitions for hosts. For each host supplied on the command
	line, this command prints the hostname and partitions for that host.

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, info about
	all the known hosts is listed.
	</arg>

	<example cmd='list host partition backend-0-0'>
	List partition info for backend-0-0.
	</example>

	<example cmd='list host partition'>
	List partition info for known hosts.
	</example>
	"""

	def run(self, params, args):
	
		self.beginOutput()
		
		for host in self.getHostnames(args):
			self.db.execute("""select 
				p.device, p.mountpoint, p.uuid, p.sectorstart,
				p.partitionsize, p.partitionid, p.fstype,
				p.partitionflags, p.formatflags from 
				partitions p, host_view hv where 
				hv.name='%s' and hv.id=p.node order by device""" %
				host)

			for row in self.db.fetchall():
				self.addOutput(host, row)

		self.endOutput(header=['host', 'device', 'mountpoint', 'uuid',
			'start', 'size', 'id', 'type', 'flags', 'formatflags'])



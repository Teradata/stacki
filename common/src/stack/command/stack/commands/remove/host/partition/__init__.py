# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands
from stack.exception import ArgRequired


class Command(stack.commands.remove.host.command):
	"""
	Remove a partition definitions from a host.

	<arg type='string' name='host' repeat='1'>
	A list of one or more host names.
	</arg>

	<param type='string' name='partition'>
	A single partition to remove from this host. If no partition is
	specified, then all partitions from the host are removed.
	</param>

	<param name="device" type="string">
	Device name to be removed
	</param>

	<param name="uuid" type="string">
	UUID of the mountpoint to be removed.
	</param>

	<example cmd='remove host partition backend-0-0'>
	Remove all partitions from backend-0-0.
	</example>

	<example cmd='remove host partition backend-0-0 partition=/export'>
	Remove only the /export partition from backend-0-0.
	</example>

	<example cmd='remove host partition backend-0-0 device=sdb1'>
	Remove only the partition information for /dev/sdb1 on backend-0-0
	</example>
	"""

	def run(self, params, args):
		if not len(args):
			raise ArgRequired(self, 'host')

		hosts = self.getHostnames(args)
		if not hosts:
			raise ArgRequired(self, 'host')

		(partition, device, uuid) = self.fillParams([
			('partition', None),
			('device', None),
			('uuid', None)
		])

		for host in hosts:
			sql = """
				delete from partitions
				where node=(select id from nodes where name=%s)
			"""
			values = [host]

			if uuid:
				sql += ' and uuid=%s'
				values.append(uuid)

			if partition:
				sql += ' and mountpoint=%s'
				values.append(partition)

			if device:
				sql += ' and device=%s'
				values.append(device)

			self.db.execute(sql, values)

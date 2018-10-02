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
from stack.exception import ParamValue


class Command(stack.commands.set.host.command):
	"""
	Set a bootaction for a host. A hosts action can be set to 'install'
	or to 'os'.

	<arg type='string' name='host' repeat='1'>
	One or more host names.
	</arg>

	<param type='string' name='action' optional='0'>
	The label name for the bootaction. This must be one of: 'os',
	'install'.
	</param>

	<param type='boolean' name='nukedisks' optional='1'>
	Set the host to erase all disks on next install. Default: False
	</param>

	<param type='boolean' name='nukecontroller' optional='1'>
	Set the host to overwrite the controller configuration on next
	install. Default: False
	</param>

	<param type='boolean' name='sync' optional='1'>
	Controls if 'sync host boot' needs to be run after setting the
	bootaction. Default: True
	</param>

	<example cmd='set host boot backend-0-0 action=os'>
	On the next boot, backend-0-0 will boot the profile based on its
	"run action".
	</example>
	"""

	def run(self, params, args):
		hosts = self.getHosts(args)

		(action, nukedisks, nukecontroller, sync) = self.fillParams([
			('action', None, True),
			('nukedisks', None, False),
			('nukecontroller', None, False),
			('sync', True)
		])

		sync = self.str2bool(sync)
		if action not in ['os', 'install']:
			raise ParamValue(self, 'action', 'one of: os, install')

		# Get the mapping of hosts with boot actions and thier PK
		hosts_with_boot = {row[0]: row[1] for row in self.db.select(
			'nodes.name, nodes.id from nodes, boot where nodes.id=boot.node'
		)}

		for host in hosts:
			if host in hosts_with_boot:
				self.db.execute(
					'update boot set action=%s where node=%s',
					(action, hosts_with_boot[host])
				)
			else:
				self.db.execute("""
					insert into boot(action, node) values (
						%s, (select id from nodes where name=%s)
					)
				""", (action, host))

		if nukedisks is not None:
			args = hosts.copy()
			args.extend([
				'attr=nukedisks', 'value=%s' % self.str2bool(nukedisks)
			])

			self.command('set.host.attr', args)

		if nukecontroller is not None:
			args = hosts.copy()
			args.extend([
				'attr=nukecontroller', 'value=%s' % self.str2bool(nukecontroller)
			])

			self.command('set.host.attr', args)

		if sync:
			self.command('sync.host.boot', hosts)

# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ParamValue, CommandError


class Command(stack.commands.set.host.command):
	"""
	Update bootaction for a host.

	<arg type='string' name='host' repeat='1'>
	One or more host names.
	</arg>

	<param type='string' name='action' optional='0'>
	bootaction name. This should already exist via 'stack list bootaction'
	</param>

	<param type='string' name='type' optional='0'>
	type of bootaction. can be one of 'os' or 'install'
	</param>

	<param type='boolean' name='sync' optional='1'>
	controls if 'sync host boot' needs to be run after
	setting the bootaction.
	</param>

	<example cmd="set host bootaction action=memtest type=os sd-stacki-131">
	sets the bootaction for sd-stacki-131 to memtest
	</example>
	"""

	def run(self, params, args):
		hosts = self.getHosts(args)

		(req_action, req_type, req_sync) = self.fillParams([
			('action', None, True),
			('type', None, True),
			('sync', True)
		])

		req_sync = self.str2bool(req_sync)
		req_type = req_type.lower()
		req_action = req_action.lower()

		if req_type not in ('os', 'install'):
			raise ParamValue(self, 'type', 'one of: os, install')

		# Make sure our bootaction exists
		if len(self.call(
			'list.bootaction',
			[req_action, 'type=%s' % req_type ]
		)) == 0:
			raise CommandError(
				self, f'bootaction "{req_action}" does not exist'
			)

		for host in hosts:
			self.db.execute(f"""
				update nodes set {req_type}action=(
					select id from bootnames where name=%s and type=%s
				)
				where nodes.name=%s
			""", (req_action, req_type, host))

		if req_sync:
			self.command('sync.host.boot', hosts)

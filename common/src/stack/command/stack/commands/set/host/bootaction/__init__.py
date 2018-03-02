# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgRequired, ParamValue, CommandError


class Command(stack.commands.set.host.command):
	"""
	Update bootaction for a host.

	<arg type='string' name='bootaction' repeat='1' optional='1'>
	Host name of machine
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

		(req_action, req_type, req_sync) = self.fillParams([
			('action', None, True),
			('type', None, True),
			('sync', True)
		])

		if not len(args):
			raise ArgRequired(self, 'host')

		req_sync   = self.str2bool(req_sync)
		req_type   = req_type.lower()
		req_action = req_action.lower()
		types      = { 'os'     : 'osaction',
			       'install': 'installaction' }

		if req_type not in types.keys():
			raise ParamValue(self, 'type', 'one of: %s' % ', '.join(types.keys()))

		exists = False
		for row in self.call('list.bootaction', [ req_action, 
							  'type=%s' % req_type ]):
			exists = True
		if not exists:
			raise CommandError(self, 'bootaction %s does not exist' % req_action)

		hosts = self.getHostnames(args)
		for host in hosts:
			self.db.execute(
				"""
				update nodes
				set 
				%s = (select id from bootnames where name='%s' and type='%s')
				where nodes.name = '%s'
				""" % (types[req_type], req_action, req_type, host))

		if req_sync:
			self.command('sync.host.boot', hosts)

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
from stack.exception import ArgRequired, ParamValue


class Command(stack.commands.set.host.command):
	"""
	Set a bootaction for a host. A hosts action can be set to 'install' 
	or to 'os' (also, 'run' is a synonym for 'os').

	<arg type='string' name='host' repeat='1'>
	One or more host names.
	</arg>

	<param type='string' name='action'>
	The label name for the bootaction. This must be one of: 'os',
	'install', or 'run'.

	If no action is supplied, then only the configuration file for the
	list of hosts will be rewritten.
	</param>
		
	<example cmd='set host boot backend-0-0 action=os'>
	On the next boot, backend-0-0 will boot the profile based on its
	"run action". To see the node's "run action", execute:
	"rocks list host backend-0-0" and examine the value in the
	"RUNACTION" column.
	</example>
	"""

	def run(self, params, args):

		if not len(args):
			raise ArgRequired(self, 'host')

		(action, nukedisks, nukecontroller, sync) = self.fillParams([
			('action', None, True),
			('nukedisks', None, False),
			('nukecontroller', None, False),
			('sync', True)
		])
		
		sync    = self.str2bool(sync)
		actions = [ 'os', 'install' ]
		if action not in actions:
			raise ParamValue(self, 'action', 'one of: %s' % ', '.join(actions))


		boot = {}
		for h, a in self.db.select(
				"""
				hv.name, b.action from 
				host_view hv, boot b where
				hv.id = b.node
				"""):
			boot[h] = a

		hosts = self.getHostnames(args)
		for host in hosts:
			if host in boot.keys():
				self.db.execute(
					"""
					update boot set action = '%s'
					where node = (select id from host_view where name = '%s')
					""" % (action, host))
			else:
				self.db.execute(
					"""
					insert into boot (action, node) values 
					(
					'%s',
					(select id from host_view where name = '%s')
					) 
					""" % (action, host))

		args = hosts.copy()
		if len(args) > 0:
			if nukedisks is not None:
				nukedisks = self.str2bool(nukedisks)
				args.extend(['attr=nukedisks', 'value=%s' % nukedisks])
				self.command('set.host.attr',args)
			if nukecontroller is not None:
				nukecontroller = self.str2bool(nukecontroller)
				args.extend(['attr=nukecontroller', 'value=%s' % nukecontroller])
				self.command('set.host.attr',args)

		if sync:
			self.command('sync.host.boot', hosts)


RollName = "stacki"

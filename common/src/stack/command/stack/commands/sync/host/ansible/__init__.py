#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import sys
import stack.commands
from stack.commands.sync.host import Parallel
from stack.commands.sync.host import timeout


class Command(stack.commands.sync.host.command):
	"""
	Sync a an ansible inventory to nodes.
	
	Syncs the same file to every node in
	/etc/ansible/hosts.

	<param type='string' name='attribute'>
	A shell syntax glob pattern to specify attributes to
	be sent to the report generator. 
	
	Create group targets in the ini file.
	</param>

	<example cmd='sync ansible backend-0-0'>
	Sync ansible inventory file on backend-0-0
	</example>

	<example cmd='sync ansible a:backend'>
	Sync ansible inventory file to all backends.
	</example>

	<example cmd='sync host ansible'>
	Giving no hostname or regex will sync
	to all backend nodes by default.
	</example>

	<example cmd='sync ansible backend-0-[0-2]'>
	Using regex, sync inventory file on backend-0-0
	backend-0-1, and backend-0-2.
	</example>
	"""

	def run(self, params, args):
		prms = self._params
		if prms:
			pkeys = list(prms.keys())[0]
			pvalues = list(prms.values())[0]

		self.notify('Sync Host Ansible Inventory\n')


		hosts = self.getHostnames(args, managed_only=0)
		run_hosts = self.getRunHosts(hosts)
		me    = self.db.getHostname('localhost')

		# Only shutdown stdout/stderr if we not local
		for host in hosts:
			if host != me:
				sys.stdout = open('/dev/null')
				sys.stderr = open('/dev/null')
				break

		threads = []
		ha = self.call('list.host.attr', hosts)
		g = lambda x: (x['attr'], x['value'])
		
		host_attrs = {}
		for host in hosts:
			if host not in host_attrs:
				host_attrs[host] = {}
			f = lambda x : x['host'] == host
			tmp_f = list(filter(f, ha))
			host_attrs[host] = dict(list(map(g, tmp_f)))

		for h in run_hosts:
			host = h['host']
			hostname = h['name']
			if prms:
				cmd = '/opt/stack/bin/stack report ansible %s ' % host
				cmd += '%s=%s | ' % (pkeys,pvalues)
			else:
				cmd = '/opt/stack/bin/stack report ansible %s | ' % host

			cmd += '/opt/stack/bin/stack report script | '

			if me != host:
				cmd += 'ssh -T -x %s ' % hostname
			cmd += 'bash > /dev/null 2>&1 '

			try:
				p = Parallel(cmd)
				p.start()
				threads.append(p)
			except:
				pass

		#
		# collect the threads
		#
		for thread in threads:
			thread.join(timeout)

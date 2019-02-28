#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
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
	Sync time configuration to backend nodes

	<example cmd='sync host time'>
	Sync time configuration for all backend hosts
	</example>

	<example cmd='sync host repo backend-0-0'>
	Sync time configuration on backend-0-0
	</example>

	<example cmd='sync repo backend-0-[0-2]'>
	Using regex, sync time configuration  on
	backend-0-0 backend-0-1, and backend-0-2.
	</example>
	"""

	def run(self, params, args):

		self.notify('Sync Host Time')


		hosts = self.getHostnames(args, managed_only=1)
		run_hosts = self.getRunHosts(hosts)
		me    = self.db.getHostname('localhost')

		# Only shutdown stdout/stderr if we not local
		for host in hosts:
			if host != me:
				sys.stdout = open('/dev/null')
				sys.stderr = open('/dev/null')
				break

		threads = []

		for h in run_hosts:
			host = h['host']
			hostname = h['name']

			cmd = '/opt/stack/bin/stack report host time %s | ' % host
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

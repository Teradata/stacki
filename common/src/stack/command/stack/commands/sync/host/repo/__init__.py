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
from stack.repo import rewrite_repofile

class Command(stack.commands.sync.host.command):
	"""
	Sync a repository configuration file to backend nodes.

	When a cart or pallet is added to the
	frontend, to use the resulting repo but not
	reinstall machines, sync the new repo to the
	backends for immediate use.

	<example cmd='sync host repo'>
	Giving no hostname or regex will sync
	to all backend nodes by default.
	</example>

	<example cmd='sync host repo backend-0-0'>
	Sync the repository inventory file on backend-0-0
	</example>

	<example cmd='sync repo backend-0-[0-2]'>
	Using regex, sync repository inventory file on backend-0-0
	backend-0-1, and backend-0-2.
	</example>
	"""

	def run(self, params, args):

		self.notify('Sync Host Repo')

		hosts = self.getHostnames(args, managed_only=1)
		me    = self.db.getHostname('localhost')

		# if we're only syncing localhost, just do that and don't mess with the other stuff
		if hosts == [me]:
			rewrite_repofile()
			return

		threads = []

		for host_data in self.getRunHosts(hosts):
			stacki_hostname, run_hostname = host_data['host'], host_data['name']

			cmd = f'/opt/stack/bin/stack report host repo {stacki_hostname} | '
			cmd += '/opt/stack/bin/stack report script | '

			if me != stacki_hostname:
				cmd += f'ssh -T -x {run_hostname} '
			cmd += 'bash > /dev/null 2>&1 '

			try:
				p = Parallel(cmd)
				p.start()
				threads.append(p)
			except:
				pass

		# collect the threads
		for thread in threads:
			thread.join(timeout)

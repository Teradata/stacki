#
# @SI_Copyright@
# @SI_Copyright@
#

import sys
import stack.commands
from stack.commands.sync.host import Parallel
from stack.commands.sync.host import timeout


class Command(stack.commands.sync.host.command):
	"""
	Sync yum repo file to backend nodes.
	
	When a cart or pallet is added to the 
	frontend, to use the resulting repo but not
        reinstall machines, sync the new repo to the 
	backends for immediate use.

	<example cmd='sync host yum'>
	Giving no hostname or regex will sync
        to all backend nodes by default.
	</example>

	<example cmd='sync host yum backend-0-0'>
	Sync yum inventory file on backend-0-0
	</example>
	
	<example cmd='sync yum backend-0-[0-2]'>
	Using regex, sync yum inventory file on backend-0-0
	backend-0-1, and backend-0-2.
	</example>
	"""

	def run(self, params, args):
		sys.stdout = open('/dev/null')
		sys.stderr = open('/dev/null')

		hosts = self.getHostnames(args, managed_only=1)
		me = self.db.getHostname('localhost')

		threads = []
		for host in hosts:
			attrs = self.db.getHostAttrs(host)

			cmd = '/opt/stack/bin/stack report host yum %s | ' % host
			cmd += '/opt/stack/bin/stack report script | '

			if me != host:
				cmd += 'ssh -T -x %s ' % host
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

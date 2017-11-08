# @copyright@
# Copyright (c) 2006 - 2017 Teradata
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
from stack.commands.sync.host import Parallel
from stack.commands.sync.host import timeout


class Command(stack.commands.sync.host.command):
	"""
	Reconfigure and optionally restart firewall for named hosts.

	<param type='boolean' name='restart'>
	If "yes", then restart iptables after the configuration files are
	applied on the host.
	The default is: yes.
	</param>

	<example cmd='sync host firewall compute-0-0'>
	Reconfigure and restart the firewall on compute-0-0.
	</example>
	"""

	def run(self, params, args):
		restart, = self.fillParams([ ('restart', 'yes') ])
		restartit = self.str2bool(restart)

		hosts = self.getHostnames(args, managed_only=1)

		me = self.db.getHostname('localhost')

		threads = []
		out = {}
		host_output = {}
		for host in hosts:

			host_output[host] = {"output": "", "error": "", "rc": 0}
			out[host] = ""
			attrs = {}
			for row in self.call('list.host.attr', [ host ]):
				attrs[row['attr']] = row['value']

			if self.str2bool(attrs.get('firewall')) is not True:
				continue

			cmd = '/opt/stack/bin/stack report host firewall '
			cmd += '%s | ' % host
			cmd += '/opt/stack/bin/stack report script '
			cmd += 'attrs="%s" | ' % attrs
			if me != host:
				cmd += 'ssh -T -x %s ' % host
			cmd += 'bash > /dev/null 2>&1 '

			p = Parallel(cmd, host_output[host])
			threads.append(p)
			p.start()
		#
		# collect the threads
		#
		for thread in threads:
			thread.join(timeout)

		for host in host_output:
			if host_output[host]["rc"]:
				out[host] += host_output[host]['output']

		if restartit:
			threads = []
			for host in hosts:
				if stack.release in [ 'redhat7', 'sles12' ]:
					cmd = 'systemctl restart iptables'
				else:
					cmd = '/sbin/service iptables restart'

				if me != host:
					cmd = 'ssh -T -x %s "%s"' % (host, cmd)
				host_output[host] = {"output": "", "error": "", "rc": 0}
				p = Parallel(cmd, host_output[host])
				threads.append(p)
				p.start()

			#
			# collect the threads
			#
			for thread in threads:
				thread.join(timeout)

		for host in host_output:
			if host_output[host]["rc"]:
				out[host] += host_output[host]['output']

		self.beginOutput()
		for host in out:
			if len(out[host]):
				self.addOutput(host, out[host])

		self.runPlugins(hosts)
		self.endOutput(header=['host', 'output'])

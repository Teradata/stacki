# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@

import os
import stack.commands
from stack.commands.sync.host import Parallel
from stack.commands.sync.host import timeout


class Command(stack.commands.sync.host.command):
	"""
	Reconfigure and optionally restart the network for the named hosts.

	<param type='boolean' name='restart'>
	If "yes", then restart the network after the configuration files are
	applied on the host.
	The default is: yes.
	</param>

	<example cmd='sync host network compute-0-0'>
	Reconfigure and restart the network on compute-0-0.
	</example>
	"""

	def run(self, params, args):
		restart, = self.fillParams([ ('restart', 'yes') ])

		restartit = self.str2bool(restart)

		hosts = self.getHostnames(args, managed_only=1)

		me = self.db.getHostname('localhost')

		threads = []
		for host in hosts:

			attrs = {}
			for row in self.call('list.host.attr', [ host ]):
				attrs[row['attr']] = row['value']

			cmd = '/opt/stack/bin/stack report host interface '
			cmd += '%s | ' % host
			cmd += '/opt/stack/bin/stack report script '
			cmd += 'attrs="%s" | ' % attrs
			if host != me:
				cmd += 'ssh -T -x %s ' % host
			cmd += 'bash > /dev/null 2>&1 '

			cmd += '; /opt/stack/bin/stack report host network '
			cmd += '%s | ' % host
			cmd += '/opt/stack/bin/stack report script '
			cmd += 'attrs="%s" | ' % attrs
			if host != me:
				cmd += 'ssh -T -x %s ' % host
			cmd += 'bash > /dev/null 2>&1 '

			cmd += '; /opt/stack/bin/stack report host route '
			cmd += '%s | ' % host
			cmd += '/opt/stack/bin/stack report script '
			cmd += 'attrs="%s" | ' % attrs
			if host != me:
				cmd += 'ssh -T -x %s ' % host
			cmd += 'bash > /dev/null 2>&1 '

			p = Parallel(cmd)
			threads.append(p)
			p.start()

		#
		# collect the threads
		#
		for thread in threads:
			thread.join(timeout)

		self.command('sync.host.firewall',
			[ 'restart=%s' % restart ] + hosts)

		self.runPlugins(hosts)

		if restartit:
			#
			# after all the configuration files have been rewritten,
			# restart the network
			#
			threads = []
			for host in hosts:
				cmd = '/sbin/service network restart '
				cmd += '> /dev/null 2>&1 ; '
				cmd += '/sbin/service ipmi restart > '
				cmd += '/dev/null 2>&1'
				if host != me:
					cmd = 'ssh %s "%s"' % (host, cmd)

				p = Parallel(cmd)
				threads.append(p)
				p.start()

			#
			# collect the threads
			#
			for thread in threads:
				thread.join(timeout)

		#
		# if IP addresses change, we'll need to sync the config (e.g.,
		# update /etc/hosts, /etc/dhcpd.conf, etc.).
		#
		self.command('sync.config')

		#
		# hack for ganglia on the frontend
		#
		if me in hosts and os.path.exists('/etc/ganglia/gmond.conf'):
			os.system('service gmond restart > /dev/null 2>&1')


# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import os
import stack.commands
import tempfile
import subprocess
import io
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

	<example cmd='sync host network backend-0-0'>
	Reconfigure and restart the network on backend-0-0.
	</example>
	"""

	def isStacki(self, filename):
		with open(filename, 'r') as f:
			for line in f:
				if '# AUTHENTIC STACKI' in line:
					return True
		return False


	def cleanup(self):
		#
		# open all the ifcfg-* files and remove the ones that were written by Stacki
		#
		# the code in the 'run' function will rebuild all the Stacki files
		#
		if self.os == 'sles':
			ifcfg_dir = '/etc/sysconfig/network'
		else:
			#TODO Ubuntu?
			ifcfg_dir = '/etc/sysconfig/network-scripts'

		for fname in os.listdir(ifcfg_dir):
			if fname != 'ifcfg-lo' and fname.startswith('ifcfg-'):
				filename = f'{ifcfg_dir}/{fname}'
				if self.isStacki(filename):
					os.remove(filename)


	def run(self, params, args):
		restart, = self.fillParams([ ('restart', 'yes') ])

		restartit = self.str2bool(restart)

		hosts = self.getHostnames(args, managed_only=1)
		run_hosts = self.getRunHosts(hosts)

		me = self.db.getHostname('localhost')

		threads = []

		for h in run_hosts:
			host = h['host']
			hostname = h['name']

			if host == me:
				self.cleanup()

			# Sometimes these return None, in that case, make them an empty string
			c = str(self.command('report.host.interface',[host]) or '') + \
				str(self.command('report.host.network',[host]) or '') + \
				str(self.command('report.host.route',[host]) or '')

			s = subprocess.Popen(['/opt/stack/bin/stack','report','script'],
				stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			o, e = s.communicate(input=c.encode())
			
			cmd = '( /opt/stack/bin/stack report host interface %s && ' % host
			cmd += '/opt/stack/bin/stack report host network %s && ' % host
			cmd += '/opt/stack/bin/stack report host route %s ) | ' % host
			cmd += '/opt/stack/bin/stack report script | '
			if host != me:
				cmd += 'ssh -T -x %s ' % hostname
			cmd += 'bash > /dev/null 2>&1'

			p = Parallel(cmd, stdin=o.decode())
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
			for h in run_hosts:
				host = h['host']
				hostname = h['name']
				cmd = '/sbin/service network restart '
				cmd += '> /dev/null 2>&1 ; '
				cmd += '/sbin/service ipmi restart > '
				cmd += '/dev/null 2>&1'
				if host != me:
					cmd = 'ssh %s "%s"' % (hostname, cmd)

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


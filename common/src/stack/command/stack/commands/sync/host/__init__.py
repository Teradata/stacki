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
import threading
import subprocess
import time
import os

max_threading = 512
timeout	= 30


class command(stack.commands.sync.command,
	stack.commands.HostArgumentProcessor):
	def getRunHosts(self, hosts):
		self.mgmt_networks = {}
		run_hosts = []
		self.attrs = self.call('list.host.attr',hosts)
		f = lambda x: x['attr'] == 'stack.network'
		network_attrs = list(filter(f, self.attrs))

		self.mgmt_networks = {}
		for host in hosts:
			g = lambda x: x['host'] == host
			s = list(filter(g, network_attrs))
			if len(s):
				network = s[0]['value']
				if network not in self.mgmt_networks:
					self.mgmt_networks[network] = []
				self.mgmt_networks[network].append(host)

		a = []
		b = []
		for net in self.mgmt_networks:
			h = self.mgmt_networks[net]
			a.extend(h)
			b.extend(self.getHostnames(h, subnet=net))

		for host in hosts:
			if host in a:
				idx = a.index(host)
				run_hosts.append({'host':host, 'name':b[idx]})
			else:
				run_hosts.append({'host':host, 'name':host})

		return run_hosts


class Parallel(threading.Thread):
	def __init__(self, cmd, out=None, stdin=None):
		self.cmd = cmd
		self.stdin = stdin
		if not out:
			self.out = {"output": "", "error": "", "rc": 0}
		else:
			self.out = out
		while threading.activeCount() > max_threading:
			time.sleep(0.001)
		threading.Thread.__init__(self)

	def run(self):
		if not self.stdin:
			p = subprocess.Popen(self.cmd,
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT,
				shell=True)
			(o, e) = p.communicate()
		else:
			p = subprocess.Popen(self.cmd,
				stdin=subprocess.PIPE,
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT,
				shell=True)
			(o, e) = p.communicate(self.stdin.encode())
		
		rc = p.wait()
		if o:
			self.out['output'] = o.decode()
		if e:
			self.out['error'] = e.decode()
		self.out['rc'] = rc


class Command(command):
	"""
	Writes the /etc/hosts file based on the configuration database
	"""

	def run(self, params, args):

		self.notify('Sync Host\n')

		output = self.command('report.host')
		f = open('/etc/hosts', 'w')
		f.write("%s\n" % output)
		f.close()

		if os.path.exists('/srv/salt/rocks'):
			f = open('/srv/salt/rocks/hosts', 'w')
			f.write("%s\n" % output)
			f.close()






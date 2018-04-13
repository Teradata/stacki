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


class command(stack.commands.HostArgumentProcessor,
	stack.commands.sync.command):
	pass


class Parallel(threading.Thread):
	def __init__(self, cmd, out=None):
		self.cmd = cmd
		if not out:
			self.out = {"output": "", "error": "", "rc": 0}
		else:
			self.out = out
		while threading.activeCount() > max_threading:
			time.sleep(0.001)
		threading.Thread.__init__(self)

	def run(self):
		p = subprocess.Popen(self.cmd,
			stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT,
			shell=True)
		(o, e) = p.communicate()
		rc = p.wait()
		self.out['output'] = o
		self.out['error'] = e
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






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
import subprocess
import threading
import time

import stack.commands
from stack.commands import HostArgProcessor

max_threading = 512
timeout	= 30


class command(HostArgProcessor, stack.commands.sync.command):
	pass

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
	Writes the /etc/hosts file on the frontend based on the configuration in the database

	<example cmd='sync host'>
	Re-writes /etc/hosts
	</example>
	"""

	def run(self, params, args):
		self.notify('Sync Host')
		self.report('report.host')

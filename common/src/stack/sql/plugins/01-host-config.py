#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
import os
import stack.sql
import subprocess

class Plugin(stack.sql.InsertEthersPlugin):
	"""
	Calls "rocks sync host config <hostname>"
	"""
	def added(self, nodename, id):
		self.sync(nodename)

	def removed(self, nodename, id):
		pass

	def update(self):
		pass

	def done(self):
		pass

	def sync(self, nodename):
		p = subprocess.Popen([
			'/opt/stack/bin/stack',
			'sync','host', 'config', nodename],
			stdout=open('/dev/null'),
			stderr=open('/dev/null'),
			)
		rc = p.wait()
		return

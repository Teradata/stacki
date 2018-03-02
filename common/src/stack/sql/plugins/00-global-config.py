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
	Calls "rocks sync config"
	"""
	def added(self, nodename, id):
		self.sync()

	def removed(self, nodename, id):
		self.sync()

	def update(self):
		self.sync()

	def done(self):
		pass

	def sync(self):
		p = subprocess.Popen([
			'/opt/stack/bin/stack','sync','config'],
			stdout=open('/dev/null'),
			stderr=open('/dev/null'),
			)
		rc = p.wait()
		return

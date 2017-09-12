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

import stack
import stack.commands


class Command(stack.commands.report.command):
	"""
	Reports hostname of the database.
	"""

	def run(self, param, args):

		# If we already know the stack.DatabaseHost just report
		# that.  Otherwise we assume we are on the database
		# host and we report the name of the private interface.

		try:
			host = stack.DatabaseHost
		except:
			host = self.db.getHostname()

		self.beginOutput()
		self.addOutput('', '<stack:file stack:name="%s/__init__.py" stack:mode="append">'
			% stack.__path__[0])
		self.addOutput('', 'DatabaseHost = "%s"' % host)
		self.addOutput('', '</stack:file>')
		self.endOutput(padChar='')



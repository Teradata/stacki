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



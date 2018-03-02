# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.discovery import Discovery


class Command(stack.commands.report.command):
	"""
	Report the status of the node discovery daemon.

	<example cmd='report discovery'>
	Report if the node discovery daemon is running.
	</example>

	<related>enable discovery</related>
	<related>disable discovery</related>
	"""		

	def run(self, params, args):
		discovery = Discovery()

		self.beginOutput()
		if discovery.is_running():
			self.addOutput('', "Discovery daemon is running")
		else:
			self.addOutput('', "Discovery daemon is stopped")
		self.endOutput()

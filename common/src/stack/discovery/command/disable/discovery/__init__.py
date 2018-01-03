# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.discovery import Discovery


class Command(stack.commands.disable.command):
	"""
	Stop the node discovery daemon.

	<example cmd='disable discovery'>
	Stop the node discovery daemon.
	</example>

	<related>enable discovery</related>
	<related>report discovery</related>
	"""		

	def run(self, params, args):
		discovery = Discovery()

		discovery.stop()

		self.beginOutput()
		self.addOutput('', "Discovery daemon has stopped")
		self.endOutput()

# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.discovery import Discovery
import time


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

		# Wait up to a few seconds for the daemon to stop
		for _ in range(8):
			# Are we done yet?
			if not discovery.is_running():
				self.beginOutput()
				self.addOutput('', "Discovery daemon has stopped")
				self.endOutput()

				break

			# Take a quarter second nap
			time.sleep(0.25)
		else:
			self.beginOutput()
			self.addOutput('', "Warning: daemon might have not stopped")
			self.endOutput()

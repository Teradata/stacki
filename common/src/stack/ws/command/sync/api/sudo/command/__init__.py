# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os
import stack.commands
import stack.commands.sync

class Command(stack.commands.sync.command):
	"""
	Sync the sudoers.d file on the frontend

	<dummy />
	"""
	def run(self, params, args):
		self.report("report.api.sudo.command")

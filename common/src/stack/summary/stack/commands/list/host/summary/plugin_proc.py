#
# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import stack.commands

class Plugin(stack.commands.Plugin):
	def provides(self):
		return "proc"

	def requires(self):
		return ["nodes"]

	def run(self, params):
		# Get number of processors
		cmd = "cat /proc/cpuinfo | grep processor | wc -l"
		d = self.owner.run_cmd(cmd)
		cpu_count = 0
		for i in d:
			cpu_count += int(d[i])

		self.owner.addOutput('localhost', ("CPU Count", cpu_count))

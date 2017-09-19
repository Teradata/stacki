#
# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import stack.commands

class Plugin(stack.commands.Plugin):
	def provides(self):
		return 'mem'

	def requires(self):
		return ["proc"]

	def run(self, params):
		# Get total memory
		cmd = "cat /proc/meminfo | grep MemTotal"
		d = self.owner.run_cmd(cmd)
		mem = 0
		for i in d:
			mem += int(d[i].split()[1])
		mem = mem/(1024**2)
		self.owner.addOutput('localhost', ("Total Memory", "%d GB" % mem))



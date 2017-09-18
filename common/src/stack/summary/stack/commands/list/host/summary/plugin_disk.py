#
# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import stack.commands
import re

class Plugin(stack.commands.Plugin):
	def provides(self):
		return "disk"

	def requires(self):
		return ['proc','mem']

	def run(self, params):
		# Get total size of discovered disks
		d = self.owner.run_cmd("cat /proc/partitions")
		
		r = re.compile("[a-z]"*3 + "$")
		disk_space = 0
		for  i in d:
			for line in d[i].split('\n'):
				try:
					s = line.index("#blocks")
					if s >= 0:
						continue
				except:
					pass
				m = r.search(line)
				if m:
					hdspace = int(line.split()[2].strip())/(1024**2)
					disk_space += hdspace

		self.owner.addOutput('localhost', ("Disk Space", "%d GB" % disk_space))



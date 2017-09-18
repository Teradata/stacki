# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os
import stack.commands


class Plugin(stack.commands.Plugin):
	"Include compiled salt templates into profile"

	def provides(self):
		return 'salt'

	def run(self, attrs):
		try:
			fin = open(os.path.join(os.sep, 'export', 
						'stack', 'salt', 
						'compiled', 
						attrs['hostname'], 
						'kickstart.xml'), 'r')
		except:
			fin = None
		if fin:
			self.owner.addText('<stack:post>\n')
			for line in fin.readlines():
				self.owner.addText(line)
			self.addText('</stack:post>\n')
		



# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import os
import stack.commands


class Implementation(stack.commands.Implementation):
	"""
	Determines if a pallet is currently mounted.
	"""
	
	def run(self, args):
		cmd = 'mount | grep %s' % self.owner.mountPoint
		if os.system(cmd):
			return False
		return True

# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import os
import stack.commands


class Implementation(stack.commands.Implementation):
	"""
	Determines if a Roll is currently mounted.
	"""
	
	def run(self, args):
		cmd = 'mount | grep %s' % self.owner.mountPoint
		if os.system(cmd):
			return False
		return True

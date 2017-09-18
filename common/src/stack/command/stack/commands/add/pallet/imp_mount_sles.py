# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import os
import stack.commands


class Implementation(stack.commands.Implementation):
	"""Mount the ISO Image on Linux"""

	def run(self, iso):
		os.system('mount -o loop %s %s > /dev/null 2>&1' % (iso, self.owner.mountPoint))
	

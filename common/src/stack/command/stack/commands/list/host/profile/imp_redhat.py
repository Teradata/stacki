# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import stack.commands
import stack.gen
import stack.redhat.gen


class Implementation(stack.commands.list.host.profile.implementation):
	def generator(self):
		return stack.redhat.gen.Generator()

# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import stack.commands.list.host.firmware

class Implementation(stack.commands.Implementation):

	def run(self, args):
		return stack.commands.list.host.firmware.imp_Mellanox_m7800.Implementation(self.owner).run(args = args)

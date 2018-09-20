# @copyright@
# Copyright (c) 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands

class Implementation(stack.commands.Implementation):

	driver_path = '/export/stack/drivers/'
	appliance = 'viewpoint'

	def run(self, args):
		return [None, None]

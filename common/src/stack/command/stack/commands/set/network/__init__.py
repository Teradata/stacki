# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.commands import NetworkArgProcessor
from stack.exception import ArgRequired, CommandError


class command(NetworkArgProcessor, stack.commands.set.command):

	def fillSetNetworkParams(self, args, paramName):
		if len(args) == 0:
			raise ArgRequired(self, 'network')

		networks = self.getNetworkNames(args)

		(param, ) = self.fillParams([
			(paramName, None, True)
		])

		return (networks, param)

# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import CommandError


class command(stack.commands.set.command,
	      stack.commands.NetworkArgumentProcessor):

	def fillSetNetworkParams(self, args, paramName):

		networks = self.getNetworkNames(args)
		if not networks:
			raise CommandError(self, 'network "%s" is not defined' % args)

		(param, ) = self.fillParams([ (paramName, None, True) ])

		return (networks, param)



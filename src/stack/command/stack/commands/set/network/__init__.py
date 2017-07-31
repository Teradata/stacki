# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

import stack.commands
from stack.exception import *

class command(stack.commands.set.command,
	      stack.commands.NetworkArgumentProcessor):

	def fillSetNetworkParams(self, args, paramName):

		networks = self.getNetworkNames(args)
		if not networks:
			raise CommandError(self, 'network "%s" is not defined' % args)

		(param, ) = self.fillParams([ (paramName, None, True) ])

		return (networks, param)



# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import CommandError

class command(stack.commands.SwitchArgumentProcessor, 
	      stack.commands.set.command):

	def fillSetSwitchParams(self, args, paramName):
		
		switches = self.getSwitchNames(args)
		if not switches:
			raise CommandError(self, 'switch "%s" is not defined' %s)

			(param,) = self.fillParams([ (paramName, None, True) ])

			return (switches, param)

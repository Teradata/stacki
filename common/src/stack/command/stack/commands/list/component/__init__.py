# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.api
import stack.commands


class command(stack.commands.ComponentArgumentProcessor,
	      stack.commands.list.command):
	pass
	

class Command(command):
	"""
	List the components

	<example cmd='list component'>
	List info for all the known components
	</example>

	"""
	def run(self, params, args):

		names     = self.getComponentNames(args)
		component = stack.api.Component()

		if names:
			self.output(component.list_multiple(names))

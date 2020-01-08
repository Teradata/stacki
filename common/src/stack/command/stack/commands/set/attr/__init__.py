# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgRequired


class Command(stack.commands.ScopeArgumentProcessor, stack.commands.set.command):
	"""
	Sets a global attribute for all nodes

	<param type='string' name='attr' optional='0'>
	Name of the attribute
	</param>

	<param type='string' name='value' optional='0'>
	Value of the attribute
	</param>

	<param type='boolean' name='shadow'>
	If set to true, then set the 'shadow' value (only readable by root
	and apache).
	</param>

	<example cmd='set attr attr=sge value=False'>
	Sets the sge attribution to False
	</example>

	<related>list attr</related>
	<related>remove attr</related>
	"""

	def run(self, params, args):
		# Get the scope and make sure the args are valid
		scope, = self.fillParams([("scope", "global")])
		self.targets_exist(scope, args)

		# Now validate the params
		attr, value, shadow, force = self.fillParams([
			('attr',   None, True),
			('value',  None, True),
			('shadow', False),
			('force',  True)
		])

		shadow = self.str2bool(shadow)
		force  = self.str2bool(force)

		if not scope == 'global' and not args:
			raise ArgRequired(self)

		# Resolve the host attributes here, since it has a bunch of more
		# logic than just matching by host name
		if scope == "host":
			args = self.getHostnames(args)

		# A set without a value is actually a remove
		if not value:
			# Remove the attribute
			self.graphql_mutation(
				f"remove_attribute(name: %s, scope: {scope}, targets: %s)",
				(attr, args)
			)
		else:
			# Add the attribute
			self.graphql_mutation(
				f"add_attribute(name: %s, value: %s, shadow: %s, force: %s, scope: {scope}, targets: %s)",
				(attr, value, shadow, force, args)
			)

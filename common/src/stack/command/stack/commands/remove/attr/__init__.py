# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands
from stack.exception import ArgRequired


class Command(stack.commands.ScopeArgumentProcessor, stack.commands.remove.command):
	"""
	Remove a global attribute.

	<param type='string' name='attr' optional='0'>
	The attribute name that should be removed.
	</param>

	<example cmd='remove attr attr=cpus'>
	Removes the global attribute named 'cpus'.
	</example>
	"""

	def run(self, params, args):
		# Get the scope and make sure the args are valid
		scope, = self.fillParams([("scope", "global")])
		self.targets_exist(scope, args)

		# Now validate the params
		attr, = self.fillParams([("attr", None, True)])

		if scope != "global" and not args:
			raise ArgRequired(self)

		# Resolve the host attributes here, since it has a bunch of more
		# logic than just matching by host name
		if scope == "host":
			args = self.getHostnames(args)

		# Remove the attribute
		self.graphql_mutation(
			f"remove_attribute(name: %s, scope: {scope}, targets: %s)",
			(attr, args)
		)

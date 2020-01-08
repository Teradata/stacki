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

import ast
from collections import defaultdict
import fnmatch
from functools import lru_cache
import os
import re

import stack.commands
from stack.bool import str2bool
from stack.exception import CommandError
from stack.util import flatten


class Command(stack.commands.ScopeArgumentProcessor, stack.commands.list.command):
	"""
	Lists the set of global attributes.

	<param type='string' name='attr'>
	A shell syntax glob pattern to specify to attributes to
	be listed.
	</param>

	<param type='boolean' name='shadow'>
	Specifies is shadow attributes are listed, the default
	is True.
	</param>

	<example cmd='list attr'>
	List the global attributes.
	</example>
	"""

	def run(self, params, args):
		# Get the scope and make sure the args are valid
		scope, = self.fillParams([('scope', 'global')])
		self.targets_exist(scope, args)

		# Now validate the params
		attr, shadow, resolve, var, const, display = self.fillParams([
			('attr',   None),
			('shadow', True),
			('resolve', True),
			('var', True),
			('const', True),
			('display', 'all'),
		])

		# Make sure bool params are bools
		resolve = self.str2bool(resolve)
		shadow = self.str2bool(shadow)
		var = self.str2bool(var)
		const = self.str2bool(const)

		# Resolve the host attributes here, since it has a bunch of more
		# logic than just matching by host name
		if scope == "host":
			args = self.getHostnames(args)

		# Get our data
		result = self.graphql_query(
			f"""attributes(
				name: %s, resolve: %s, const: %s, var: %s,
				shadow: %s, scope: {scope}, targets: %s
			)""",
			[attr, resolve, const, var, shadow, args],
			fields=["target", "scope", "type", "name", "value"]
		)

		output = defaultdict(dict)
		for row in result["attributes"]:
			value = row["value"]
			if row["name"] in {"pallets", "carts"}:
				value = ast.literal_eval(value)

			output[row["target"]][row["name"]] = [
				row["scope"], row["type"], row["name"], value
			]

		# Handle the display parameter if we are host scoped
		self.beginOutput()
		if scope == 'host' and display in {'common', 'distinct'}:
			# Construct a set of attr (name, value) for each target
			host_attrs = {}
			for target in output:
				host_attrs[target] = {
					(row[2], str(row[3])) for row in output[target].values()
				}

			common_attrs = set.intersection(*host_attrs.values())

			if display == 'common':
				for name, value in sorted(common_attrs):
					self.addOutput('_common_', [None, None, name, value])

			elif display == 'distinct':
				common_attr_names = set(v[0] for v in common_attrs)

				for target in sorted(output.keys()):
					for key in sorted(output[target].keys()):
						if key not in common_attr_names:
							self.addOutput(target, output[target][key])
		else:
			# Output our combined attributes, sorting them by target then attr
			for target in sorted(output.keys()):
				for key in sorted(output[target].keys()):
					self.addOutput(target, output[target][key])

		if scope == "global":
			self.endOutput(header=['', 'scope', 'type', 'attr', 'value'], trimOwner=True)
		else:
			self.endOutput(header=[scope, 'scope', 'type', 'attr', 'value'])

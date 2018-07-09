# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import csv
import re
from io import StringIO
import stack.commands
import stack.attr


class Command(stack.commands.Command,
	stack.commands.HostArgumentProcessor):
	"""
	This command outputs all the attributes
	of a system in a CSV format.

	<param name="filter" type="string" optional="1">
	Filter out only the attributes that you want.
	</param>
	"""

	def run(self, params, args):

		(attr_filter, ) = self.fillParams([ ("filter", None), ])

		header		= []
		csv_attrs	= []
		regex		= None

		scope_data = {}

		if attr_filter:
			regex = re.compile(attr_filter)

		#iterate through each scope and get the respective data
		for scope in [ 'global', 'os', 'appliance', 'environment', 'host' ]:
			for row in self.call('list.attr', [ 'scope=%s' % scope, 'resolve=false', 'const=false', 'shadow=false' ]):
				if scope == 'global':
					target = 'global'
				else:
					target = row[scope]
				attr   = row['attr']
				value  = row['value']

				#ignore attrs with empty values
				if value is None:
					continue
				if regex and not regex.match(attr):
					continue

				if target not in scope_data:
					scope_data[target] = {}
				scope_data[target][attr] = value

				if attr not in header:
					header.append(attr)

		for scope in scope_data:
			scope_data[scope]['target'] = scope
			csv_attrs.append(scope_data[scope])

		header.sort()
		header.insert(0, 'target')

		s = StringIO()
		w = csv.DictWriter(s, header)
		w.writeheader()
		w.writerows(csv_attrs)

		self.beginOutput()
		self.addOutput(None, s.getvalue().strip())
		self.endOutput(trimOwner = True)


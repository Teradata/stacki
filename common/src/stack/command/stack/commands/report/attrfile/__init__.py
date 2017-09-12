# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
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

		if attr_filter:
			regex = re.compile(attr_filter)


		for scope in [ 'global', 'os', 'appliance', 'environment', 'host' ]:
			for row in self.call('list.attr', [ 'scope=%s' % scope, 'resolve=false', 'const=false', 'shadow=false' ]):
				if scope == 'global':
					target = 'global'
				else:
					target = row[scope]
				attr   = row['attr']
				value  = row['value']

				if regex and regex.match(attr):
					continue

				csv_attrs.append({'target': target, attr: value})
				if attr not in header:
					header.append(attr)

		header.sort()
		header.insert(0, 'target')

		s = StringIO()
		w = csv.DictWriter(s, header)
		w.writerows(csv_attrs)

		self.beginOutput()
		self.addOutput(None, s.getvalue().strip())
		self.endOutput()

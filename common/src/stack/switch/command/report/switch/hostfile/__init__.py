# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import csv
from io import StringIO


class Command(stack.commands.Command, stack.commands.HostArgumentProcessor):
	"""
	Outputs a switch host file in CSV format.
	<dummy />
	"""

	def run(self, params, args):

		header = ['NAME', 'SWITCH', 'PORT']

		s = StringIO()
		w = csv.writer(s)
		w.writerow(header)

		for row in self.call('list.switch.host'):
			w.writerow([row['host'], row['switch'], row['port']])

		self.beginOutput()
		self.addOutput('', s.getvalue().strip())
		self.endOutput()

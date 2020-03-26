# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import csv
from io import StringIO

import stack.commands
from stack.commands import HostArgProcessor

class Command(HostArgProcessor, stack.commands.Command):
	"""
	Outputs a switch hostfile in CSV format.
	<dummy />
	"""

	def run(self, params, args):

		header = ['NAME', 'SWITCH', 'PORT', 'INTERFACE']

		s = StringIO()
		w = csv.writer(s)
		w.writerow(header)

		for row in self.call('list.switch.host'):
			w.writerow([row['host'], row['switch'], row['port'], row['interface']])

		self.beginOutput()
		self.addOutput('', s.getvalue().strip())
		self.endOutput()

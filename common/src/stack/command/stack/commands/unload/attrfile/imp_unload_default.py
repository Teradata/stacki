# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.csv
import stack.commands
from stack.exception import CommandError


class Implementation(stack.commands.ApplianceArgumentProcessor,
	stack.commands.HostArgumentProcessor, stack.commands.Implementation):	

	"""
	Create a dictionary of attributes based on comma-separated formatted
	file.
	"""

	def run(self, args):
		filename, = args

		reader = stack.csv.reader(open(filename, 'rU'))
		header = next(reader)

		appliances = self.getApplianceNames()

		for row in reader:
			target = None
			attrs = {}
			for i in range(0, len(row)):
				field = row[i]
				if header[i] == 'target':
					target = field
				elif field:
					attrs[header[i]] = field

			if target != 'global' and target not in appliances:
				host = self.db.getHostname(target)
				if not host:
					raise CommandError(self.owner, 'target "%s" is not an known appliance or host name' % host)

			if target not in self.owner.attrs.keys():
				self.owner.attrs[target] = {}

			self.owner.attrs[target].update(attrs)

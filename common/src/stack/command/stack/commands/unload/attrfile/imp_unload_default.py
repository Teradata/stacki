# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.csv
import stack.commands
from stack.commands import ApplianceArgProcessor, HostArgProcessor
from stack.exception import CommandError


class Implementation(ApplianceArgProcessor, HostArgProcessor, stack.commands.Implementation):

	"""
	Create a dictionary of attributes based on comma-separated formatted
	file.
	"""

	def run(self, args):
		filename, = args

		try:
			reader = stack.csv.reader(open(filename, encoding='ascii'))
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
					# This will raise a CommandError if the target isn't a valid host
					self.db.getHostname(target)

				if target not in self.owner.attrs.keys():
					self.owner.attrs[target] = {}

				self.owner.attrs[target].update(attrs)
		except UnicodeDecodeError:
			raise CommandError(self.owner, 'non-ascii character in file')

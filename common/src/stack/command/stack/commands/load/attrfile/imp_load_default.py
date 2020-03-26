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
			reader = stack.csv.reader(open(filename, encoding='ascii'), False)

			# Skip all header line until col[0] == 'target'
			for header in reader:
				if header[0].lower() == 'target':
					break
			else:
				raise CommandError(self.owner, "'target' must be the first column in headers")

			default = {}

			for attr in header:
				self.owner.checkAttr(attr)

			reserved = self.getApplianceNames()
			reserved.append('global')
			reserved.append('default')

			attrVal  = None
			attrName = None

			for row in reader:
				target = None
				attrs = {}

				for i in range(0, len(row)):
					field = row[i]

					if header[i] == 'target':
						target = field
					elif header[i] == 'attrName':
						attrName = field
					elif header[i] == 'attrVal':
						attrVal = field
					else:
						attrs[header[i]] = field

					if attrVal:
						attrs[attrName] = attrVal
						attrVal  = None
						attrName = None

				if target == 'default':
					default = attrs
				else:
					for key in default.keys():
						if not attrs[key]:
							attrs[key] = default[key]
				if target not in reserved:
					host = self.db.getHostname(target)
					
				if target not in self.owner.attrs.keys():
					self.owner.attrs[target] = {}

				self.owner.attrs[target].update(attrs)
		except UnicodeDecodeError:
			raise CommandError(self.owner, 'non-ascii character in file')

		# If there is a global environment specified make
		# sure each host is in that environment.
		try:
			env = self.owner.attrs['global']['environment']
		except:
			env = None
		if env:
			self.owner.call('set.host.environment',
				[ target, 'environment=%s' % env ])

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

		reader = stack.csv.reader(open(filename, 'rU'), False)

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
				self.owner.checkValue(field)
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
				if not host:
					raise CommandError(self.owner, 'target "%s" is not an known appliance or host name' % host)

			if target not in self.owner.attrs.keys():
				self.owner.attrs[target] = {}

			self.owner.attrs[target].update(attrs)

		# If there is a global environment specified make
		# sure each host is in that environment.
		
		try:
			env = self.owner.attrs['global']['environment']
		except:
			env = None
		if env:
			self.owner.call('set.host.environment',
				[ target, 'environment=%s' % env ])


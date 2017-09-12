# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

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

		# Skip all header line until col[0] == 'target'

		while True:
			header = reader.next()
			if len(header):
				target = header[0].lower()
				if target == 'target':
					break

		# Fix the header to be lowercase and strip out any
		# leading or trailing whitespace.

		for i in range(0, len(header)):
			header[i] = header[i].lower()


		default = {}

		for attr in header:
			self.owner.checkAttr(attr)

		reserved = self.getApplianceNames()
		reserved.append('global')
		reserved.append('default')

		for row in reader:

			target = None
			attrs = {}
			for i in range(0, len(row)):
				field = row[i]
				self.owner.checkValue(field)
				if header[i] == 'target':
					target = field
				else:
					attrs[header[i]] = field

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


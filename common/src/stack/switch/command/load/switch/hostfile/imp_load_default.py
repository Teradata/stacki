# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.csv
import stack.commands
from stack.bool import str2bool
from stack.exception import CommandError


class Implementation(stack.commands.ApplianceArgumentProcessor,
	stack.commands.HostArgumentProcessor,
	stack.commands.Implementation):	

	"""
	Load host into the database based on comma-separated formatted
	file.
	"""

	def run(self, args):
		filename, = args

		reader = stack.csv.reader(open(filename, 'rU'))

		header = None
		for row in reader:

			if not header:
				header = row

				#
				# make checking the header easier
				#
				required = [ 'name', 'switch', 'port' ]

				for i in range(0, len(row)):
					if header[i] in required:
						required.remove(header[i])

				if len(required) > 0:
					msg = 'the following required fields are not present in the input file: "%s"' % ', '.join(required)	
					raise CommandError(self.owner, msg)

				continue

			name = None
			switch= None
			port = None

			for i in range(0, len(row)):
				field = row[i]
				if not field:
					continue

				if header[i] == 'name':
					name = field.lower()
				if header[i] == 'switch':
					switch = field
				if header[i] == 'port':
					port = field
						
			if not name:
				msg = 'empty host name found in "name" column'
				raise CommandError(self.owner, msg)

			if not switch:
				msg = 'empty switch name found in "switch" column'
				raise CommandError(self.owner, msg)

			if switch not in self.owner.switches:
				msg = """switch named "%s" not found in database.
					 Add the switch with "add switch" command.
					 """ % switch
				raise CommandError(self.owner, msg)

			if not port:
				msg = 'empty host port found in "port" column'
				raise CommandError(self.owner, msg)

			if not port.isnumeric():
				msg = 'Port "%s" is not numeric' % port
				raise CommandError(self.owner, msg)
				



			if name not in self.owner.hosts.keys():
				self.owner.hosts[name] = {}
				self.owner.hosts[name]['host'] = name
				self.owner.hosts[name]['switch'] = switch
				self.owner.hosts[name]['port'] = port


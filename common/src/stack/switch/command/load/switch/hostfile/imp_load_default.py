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

			# If the header hasn't been set, set it
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

			# Set default values to Null so it's easier to check if they
			# didn't get assigned
			name		= None
			switch		= None
			port		= None
			interface	= None

			# Set the appropriate variables
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
				if header[i] == 'interface':
					interface = field

			# Check for any missing values that are required
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



			# If the host hasn't been assigned values, assign them
			switch_host = {'host': name, 'switch': switch, 'port': port, 'interface': interface}

			if name not in self.owner.hosts.keys():
				self.owner.hosts[name] = []
			if switch_host not in self.owner.hosts[name]:
				self.owner.hosts[name].append(switch_host)


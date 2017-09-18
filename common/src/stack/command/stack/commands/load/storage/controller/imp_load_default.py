# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#


import stack.csv
import stack.commands
from stack.exception import CommandError


class Implementation(stack.commands.ApplianceArgumentProcessor,
	stack.commands.HostArgumentProcessor,
	stack.commands.NetworkArgumentProcessor,
	stack.commands.Implementation):	

	"""
	Put storage controller configuration into the database based on
	a comma-separated formatted file.
	"""

	def doit(self, host, slot, enclosure, adapter, raid, array, options,
			line):
		#
		# error checking
		#
		if slot is None:
			msg = 'empty value found for "slot" column at line %d' % line
			CommandError(self.owner, msg)
		if raid is None:
			msg = 'empty value found for "raid level" column at line %d' % line
			CommandError(self.owner, msg)
		if array is None:
			msg = 'empty value found for "array id" column at line %d' % line
			CommandError(self.owner, msg)

		if host not in self.owner.hosts.keys():
			self.owner.hosts[host] = {}

		if array not in self.owner.hosts[host].keys():
			self.owner.hosts[host][array] = {}

		if options:
			self.owner.hosts[host][array]['options'] = options

		if enclosure:
			self.owner.hosts[host][array]['enclosure'] = enclosure

		if adapter:
			self.owner.hosts[host][array]['adapter'] = adapter

		if slot == '*' and raid != 0:
			msg = 'raid level must be "0" when slot is "*". See line %d' % (line)
			CommandError(self.owner, msg)

		if 'slot' not in self.owner.hosts[host][array].keys():
			self.owner.hosts[host][array]['slot'] = []

		if raid == 'hotspare' and array == 'global':
			if 'global' not in self.owner.hosts[host].keys():
				self.owner.hosts[host][array] = []

			if 'hotspare' not in self.owner.hosts[host][array].keys():
				self.owner.hosts[host][array]['hotspare'] = []

			self.owner.hosts[host][array]['hotspare'].append(slot)
			
		else:
			if slot in self.owner.hosts[host][array]['slot']:
				msg = 'duplicate slot "%s" found in the spreadsheet at line %d' % (slot, line)
				CommandError(self.owner, msg)

			if raid == 'hotspare':
				if 'hotspare' not in self.owner.hosts[host][array].keys():
					self.owner.hosts[host][array]['hotspare'] = []
				self.owner.hosts[host][array]['hotspare'].append(slot)
			else:
				self.owner.hosts[host][array]['slot'].append(slot)

				if 'raid' not in self.owner.hosts[host][array].keys():
					self.owner.hosts[host][array]['raid'] = raid

				if raid != self.owner.hosts[host][array]['raid']:
					msg = 'RAID level mismatch "%s" found in the spreadsheet at line %d' % (raid, line)
					CommandError(self.owner, msg)


	def run(self, args):
		filename, = args

		self.appliances = self.getApplianceNames()

		reader = stack.csv.reader(open(filename, 'rU'))
		header = None
		line = 0

		name = None

		for row in reader:
			line += 1

			if not header:
				header = row

				#
				# make checking the header easier
				#
				required = [ 'name', 'slot', 'raid level', 'array id' ]

				for i in range(0, len(row)):
					if header[i] in required:
						required.remove(header[i])

				if len(required) > 0:
					msg = 'the following required fields are not present in the input file: "%s"' % ', '.join(required)	
					CommandError(self.owner, msg)

				continue

			slot = None
			raid = None
			array = None
			options = None
			enclosure = None
			adapter = None

			for i in range(0, len(row)):
				field = row[i]
				if not field:
					continue

				if header[i] == 'name':
					name = field.lower()

				elif header[i] == 'slot':
					if field == '*':
						slot = field
					else:
						try:
							slot = int(field)
						except:
							msg = 'slot "%s" must be an integer' % field
							CommandError(self.owner, msg)

						if slot < 0:
							msg = 'slot "%d" must be 0 or greater' % slot
							CommandError(self.owner, msg)

				elif header[i] == 'raid level':
					raid = field.lower()

				elif header[i] == 'array id':
					if field.lower() == 'global':
						array = field.lower()
					elif field == '*':
						array = '*'
					else:
						try:
							array = int(field)
						except:
							msg = 'array "%s" must be an integer' % field
							CommandError(self.owner, msg)

						if array < 0:
							msg = 'array "%d" must be 0 or greater' % array
							CommandError(self.owner, msg)

				elif header[i] == 'options':
					if field:
						options = field

				elif header[i] == 'enclosure':
					if field:
						enclosure = field

				elif header[i] == 'adapter':
					if field:
						adapter = field

			#
			# the first non-header line must have a host name
			#
			if line == 1 and not name:
				msg = 'empty host name found in "name" column'
				CommandError(self.owner, msg)

			if name in self.appliances or name == 'global':
				hosts = [ name ]
			else:
				hosts = self.getHostnames([ name ])

			if not hosts:
				msg = 'Cannot find "%s"' % name
				CommandError(self.owner, msg)

			for host in hosts:
				self.doit(host, slot, enclosure, adapter,
					raid, array, options, line)

		#
		# do final validation
		#
		for host in self.owner.hosts.keys():
			for array in self.owner.hosts[host].keys():
				if array != 'global' and len(self.owner.hosts[host][array]['slot']) == 0:

					msg = 'hotspare for "%s" for array "%s" is not associated with a disk array' % (host, array)
					CommandError(self.owner, msg)


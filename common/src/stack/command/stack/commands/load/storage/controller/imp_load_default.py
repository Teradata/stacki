# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#


import stack.csv
import stack.commands
from stack.exception import CommandError


class Implementation(stack.commands.ApplianceArgumentProcessor,
                     stack.commands.HostArgumentProcessor,
                     stack.commands.NetworkArgumentProcessor,
                     stack.commands.EnvironmentArgumentProcessor,
                     stack.commands.Implementation):
	"""Put storage controller configuration into the database based on a comma-separated formatted file."""

	def doit(self, host, slot, enclosure, adapter, raid, array, options, line):
		"""Error checking and setting defaults."""
		if slot is None:
			msg = 'empty value found for "slot" column at line %d' % line
			raise CommandError(self.owner, msg)
		if raid is None:
			msg = 'empty value found for "raid level" column at line %d' % line
			raise CommandError(self.owner, msg)
		if array is None:
			msg = 'empty value found for "array id" column at line %d' % line
			raise CommandError(self.owner, msg)

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
			msg = 'raid level must be "0" when slot is "*". See line %d' % line
			raise CommandError(self.owner, msg)

		if 'slot' not in self.owner.hosts[host][array].keys():
			self.owner.hosts[host][array]['slot'] = []

		if raid == 'hotspare' and array == 'global':
			if 'global' not in self.owner.hosts[host].keys():
				self.owner.hosts[host][array] = []

			if 'hotspare' not in self.owner.hosts[host][array].keys():
				self.owner.hosts[host][array]['hotspare'] = []

			self.owner.hosts[host][array]['hotspare'].append(slot)
			
		else:
			# Slot and enclosure may have been reused in another array, so we need to check all of them
			for each_array in self.owner.hosts[host]:
				if slot in self.owner.hosts[host][each_array]['slot'] \
						and enclosure in self.owner.hosts[host][each_array]['enclosure']:
					msg = 'Enclosure "%s" and slot "%s" is already utilized in array "%s", error found in the ' \
					      'spreadsheet at line %d ' % (enclosure, slot, each_array, line)
					raise CommandError(self.owner, msg)

			if raid == 'hotspare':
				if 'hotspare' not in self.owner.hosts[host][array].keys():
					self.owner.hosts[host][array]['hotspare'] = []
				self.owner.hosts[host][array]['hotspare'].append(slot)
			else:
				self.owner.hosts[host][array]['slot'].append(slot)

				if 'raid' not in self.owner.hosts[host][array].keys():
					self.owner.hosts[host][array]['raid'] = raid

				if raid != self.owner.hosts[host][array]['raid']:
					msg = 'RAID level mismatch "%s", error found in the spreadsheet at line %d' % (raid, line)
					raise CommandError(self.owner, msg)

	def run(self, args):
		"""Run default load implementation."""
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
				required = ['name', 'slot', 'raid level', 'array id']

				for i in range(0, len(row)):
					if header[i] in required:
						required.remove(header[i])

				if len(required) > 0:
					msg = 'the following required fields are not present in the input file: "%s"' % ', '.join(required)	
					raise CommandError(self.owner, msg)

				continue

			slot = None
			raid = None
			array = None
			options = None
			enclosure = None
			adapter = None
			scope = None

			for i in range(0, len(row)):
				field = row[i]
				if not field:
					continue

				if header[i] == 'name':
					name = field.lower()
				elif header[i] == 'scope':
					scope = field.lower()
				elif header[i] == 'slot':
					if field == '*':
						slot = field
					else:
						try:
							slot = int(field)
						except TypeError or ValueError:
							msg = 'slot "%s" must be an integer' % field
							raise CommandError(self.owner, msg)

						if slot < 0:
							msg = 'slot "%d" must be 0 or greater' % slot
							raise CommandError(self.owner, msg)

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
						except TypeError or ValueError:
							msg = 'array "%s" must be an integer' % field
							raise CommandError(self.owner, msg)

						if array < 0:
							msg = 'array "%d" must be 0 or greater' % array
							raise CommandError(self.owner, msg)

				elif header[i] == 'options':
					if field:
						options = field

				elif header[i] == 'enclosure':
					if field:
						enclosure = field

				elif header[i] == 'adapter':
					if field:
						adapter = field

			# the first non-header line must have a host name
			if line == 1 and name is None:
				msg = 'empty host name found in "name" column'
				raise CommandError(self.owner, msg)
			# If scope is global, no name is allowed, coerce to global
			if scope == 'global':
				name = 'global'
				hosts = [name]
			if name in self.appliances:
				hosts = [name]
			# New logic for scope options
			elif scope is not None or scope != 'host':
				hosts = [name]
			else:
				hosts = self.getHostnames([name])

			if not hosts:
				msg = 'Cannot find "%s"' % name
				raise CommandError(self.owner, msg)

			for host in hosts:
				self.doit(host, slot, enclosure, adapter, raid, array, options, line)

		# do final validation
		for host in self.owner.hosts.keys():
			for array in self.owner.hosts[host].keys():
				if array != 'global' and len(self.owner.hosts[host][array]['slot']) == 0:
					msg = 'hotspare for "%s" for array "%s" is not associated with a disk array' % (host, array)
					raise CommandError(self.owner, msg)

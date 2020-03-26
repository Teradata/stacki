# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.csv
import stack.commands
from stack.commands import ApplianceArgProcessor
from stack.exception import CommandError


class Implementation(ApplianceArgProcessor, stack.commands.Implementation):
	"""
	Put storage controller configuration into the database based on
	a comma-separated formatted file.
	"""

	def process_target(self, host, slot, enclosure, adapter, raid, array, options, line):
		if slot is None:
			raise CommandError(
				self.owner,
				f'empty value found for "slot" column at line {line}'
			)

		if raid is None:
			raise CommandError(
				self.owner,
				f'empty value found for "raid level" column at line {line}'
			)

		if array is None:
			raise CommandError(
				self.owner,
				f'empty value found for "array id" column at line {line}'
			)

		if host not in self.owner.hosts:
			self.owner.hosts[host] = {}

		if array not in self.owner.hosts[host]:
			self.owner.hosts[host][array] = {}

		if options:
			self.owner.hosts[host][array]['options'] = options

		if enclosure:
			self.owner.hosts[host][array]['enclosure'] = enclosure

		if adapter:
			self.owner.hosts[host][array]['adapter'] = adapter

		if slot == '*' and raid not in [ '0', '1' ]:
			raise CommandError(
				self.owner,
				f'raid level must be "0" or "1" when slot is "*". See line {line}'
			)

		if 'slot' not in self.owner.hosts[host][array]:
			self.owner.hosts[host][array]['slot'] = []

		if slot in self.owner.hosts[host][array]['slot']:
			raise CommandError(
				self.owner,
				f'duplicate slot "{slot}" found in the '
				f'spreadsheet at line {line}'
			)

		if raid == 'hotspare':
			if 'hotspare' not in self.owner.hosts[host][array]:
				self.owner.hosts[host][array]['hotspare'] = []

			self.owner.hosts[host][array]['hotspare'].append(slot)
		else:
			self.owner.hosts[host][array]['slot'].append(slot)

			if 'raid' not in self.owner.hosts[host][array]:
				self.owner.hosts[host][array]['raid'] = raid

			if raid != self.owner.hosts[host][array]['raid']:
				raise CommandError(
					self.owner,
					f'RAID level mismatch "{raid}" found in the '
					f'spreadsheet at line {line}'
				)

	def run(self, args):
		filename, = args

		appliances = self.getApplianceNames()

		try:
			reader = stack.csv.reader(open(filename, encoding='ascii'))

			header = None
			name = None

			for line, row in enumerate(reader, 1):
				if line == 1:
					missing = {'name', 'slot', 'raid level', 'array id'}.difference(row)
					if missing:
						raise CommandError(
							self.owner,
							f'the following required fields are not present in '
							f'the input file: {", ".join(sorted(missing))}'
						)

					header = row
					continue

				slot = None
				raid = None
				array = None
				options = None
				enclosure = None
				adapter = None

				for ndx, field in enumerate(row):
					if not field:
						continue

					if header[ndx] == 'name':
						name = field.lower()

					elif header[ndx] == 'slot':
						if field == '*':
							slot = '*'
						else:
							try:
								slot = int(field)
							except:
								raise CommandError(
									self.owner,
									f'slot "{field}" must be an integer'
								)

							if slot < 0:
								raise CommandError(
									self.owner,
									f'slot "{slot}" must be >= 0'
								)

					elif header[ndx] == 'raid level':
						raid = field.lower()

					elif header[ndx] == 'array id':
						if field.lower() == 'global':
							array = 'global'
						elif field == '*':
							array = '*'
						else:
							try:
								array = int(field)
							except:
								raise CommandError(
									self.owner,
									f'array id "{field}" must '
									f'be an integer'
								)

							if array < 0:
								raise CommandError(
									self.owner,
									f'array id "{array}" must be >= 0'
								)

					elif header[ndx] == 'options':
						options = field

					elif header[ndx] == 'enclosure':
						enclosure = field

					elif header[ndx] == 'adapter':
						adapter = field

				if not name:
					raise CommandError(
						self.owner,
						'empty host name found in "name" column'
					)

				if name in appliances or name == 'global':
					targets = [name]
				else:
					targets = self.owner.getHostnames([name])

				if not targets:
					raise CommandError(self.owner, f'Cannot find host "{name}"')

				for target in targets:
					self.process_target(
						target, slot, enclosure, adapter,
						raid, array, options, line
					)
		except UnicodeDecodeError:
			raise CommandError(self.owner, 'non-ascii character in file')

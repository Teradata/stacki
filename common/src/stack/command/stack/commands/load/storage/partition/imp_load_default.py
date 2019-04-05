# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import re

import stack.csv
import stack.commands
from stack.exception import CommandError


class Implementation(
	stack.commands.OSArgumentProcessor,
	stack.commands.ApplianceArgumentProcessor,
	stack.commands.Implementation
):
	"""
	Put storage partition configuration into the database based on
	a comma-separated formatted file.
	"""

	def process_target(self, target, device, partid, mountpoint, size, fstype, options, line):
		if device is None:
			raise CommandError(
				self.owner,
				f'empty value found for "device" column at line {line}'
			)

		if size is None:
			raise CommandError(
				self.owner,
				f'empty value found for "size" column at line {line}'
			)

		if target not in self.owner.hosts:
			self.owner.hosts[target] = {}

		if device not in self.owner.hosts[target]:
			self.owner.hosts[target][device] = []

		self.owner.hosts[target][device].append({
			'mountpoint': mountpoint,
			'size': size,
			'type': fstype,
			'options': options,
			'partid': partid
		})

	def run(self, args):
		filename, = args

		appliances = self.getApplianceNames()
		oses = self.getOSNames()

		try:
			reader = stack.csv.reader(open(filename, encoding='ascii'))

			header = None
			name = None
			auto_partid = 0

			for line, row in enumerate(reader, 1):
				if line == 1:
					missing = {'name', 'device', 'size'}.difference(row)
					if missing:
						raise CommandError(
							self.owner,
							f'the following required fields are not present in '
							f'the input file: {", ".join(sorted(missing))}'
						)

					header = row
					continue

				auto_partid += 1

				device = None
				mountpoint = None
				size = None
				fstype = None
				options = None
				partid = None

				for ndx, field in enumerate(row):
					if not field:
						continue

					if header[ndx] == 'name':
						new_name = field.lower()

						# When the name changes we reset the auto_partid
						if new_name != name:
							auto_partid = 1

						name = new_name

					elif header[ndx] == 'device':
						device = field.lower()

					elif header[ndx] == 'mountpoint':
						mountpoint = field.lower()

					elif header[ndx] == 'size':
						if field.lower() in ['recommended', 'hibernation']:
							size = field.lower()
						else:
							try:
								size = int(field)
							except:
								raise CommandError(
									self.owner,
									f'size "{field}" must be an integer'
								)

							if size < 0:
								raise CommandError(
									self.owner,
									f'size "{size}" must be >= 0'
								)

					elif header[ndx] == 'type':
						fstype = field.lower()

					elif header[ndx] == 'options':
						options = field

					elif header[ndx] == 'partid':
						try:
							partid = int(field)
						except:
							raise CommandError(
								self.owner,
								f'partid "{field}" must be an integer'
							)

						if partid < 0:
							raise CommandError(
								self.owner,
								f'partid "{partid}" must be >= 0'
							)

				# The first non-header line must have a host name
				if line == 2 and not name:
					raise CommandError(
						self.owner,
						'empty host name found in "name" column'
					)

				# Figure out our targets
				if name in appliances or name in oses or name == 'global':
					targets = [name]
				else:
					targets = self.owner.getHostnames([name])

				if not targets:
					raise CommandError(self.owner, f'Cannot find host "{name}"')

				# If we weren't given a partid use the auto-generated one
				if not partid:
					partid = auto_partid

				for target in targets:
					self.process_target(
						target, device, partid, mountpoint,
						size, fstype, options, line
					)

		except UnicodeDecodeError:
			raise CommandError(self.owner, 'non-ascii character in file')

		# Now that we've processed the spreadsheet, do some sanity checks
		md_regex = re.compile(r'md[0-9]+')
		hd_regex = re.compile(r'xvd[a-z]+|[shv]d[a-z]+|nvme[0-9]+n[0-9]+')

		for target, devices in self.owner.hosts.items():
			# Construct some loopup tables based on mount point
			raid_devices = set()
			lvm_devices = set()
			volgroup_devices = set()

			for partitions in devices.values():
				for partition in partitions:
					if partition.get('type') == 'raid':
						raid_devices.add(partition['mountpoint'])
					elif partition.get('type') == 'lvm':
						lvm_devices.add(partition['mountpoint'])
					elif partition.get('type') == 'volgroup':
						volgroup_devices.add(partition['mountpoint'])

			# Check the devices for this target
			valid_devices = set()
			for device, partitions in devices.items():
				# Make sure software raid devices have valid options
				if md_regex.fullmatch(device):
					for partition in partitions:
						# Gotta have options
						if not partition.get('options'):
							raise CommandError(
								self.owner,
								f'missing options for software raid device "{device}"'
							)

						# First part of options needs to define the RAID level
						parts = partition['options'].split()
						if not parts[0].startswith("--level=RAID"):
							raise CommandError(
								self.owner,
								f'missing "--level=RAID" option for software raid device "{device}"'
							)

						# The other parts need to be valid RAID devices
						for part in parts[1:]:
							if part not in raid_devices:
								raise CommandError(
									self.owner,
									f'device "{part}" not defined for software raid device "{device}"'
								)

					valid_devices.add(device)

				# Physical devices are valid
				elif hd_regex.fullmatch(device):
					valid_devices.add(device)

				# Partitions inside an LVM volume groups need names
				elif device in volgroup_devices:
					for partition in partitions:
						options = partition.get('options')
						if not options or "--name=" not in options:
							raise CommandError(
								self.owner,
								f'missing "--name" option for LVM partition "{partition["mountpoint"]}"'
							)

					valid_devices.add(device)

				else:
					for partition in partitions:
						# LVM volume groups need LVM devices
						if partition['type'] == 'volgroup':
							if device not in lvm_devices:
								raise CommandError(
									self.owner,
									f'device "{device}" not defined for volgroup "{partition["mountpoint"]}"'
								)

							valid_devices.add(device)

			# Make sure all the devices for this host have been validated
			unknown_devices = set(devices.keys()).difference(valid_devices)
			if unknown_devices:
				raise CommandError(self.owner, f"unknown device(s) detected: {','.join(unknown_devices)}")

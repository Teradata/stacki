# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import re
import stack.csv
import stack.commands
from stack.exception import CommandError


class Implementation(stack.commands.ApplianceArgumentProcessor,
	stack.commands.HostArgumentProcessor,
	stack.commands.NetworkArgumentProcessor,
	stack.commands.Implementation):	

	"""
	Put storage partition configuration into the database based on
	a comma-separated formatted file.
	"""

	def doit(self, host, device, partid, mountpoint, size, fstype,
			options, line):

		#
		# error checking
		#
		if device is None:
			msg = 'empty value found for "device" column at line %d' % line
			raise CommandError(self.owner, msg)
		if size is None:
			msg = 'empty value found for "size" column at line %d' % line
			raise CommandError(self.owner, msg)
		if host not in self.owner.hosts.keys():
			self.owner.hosts[host] = {}
		
		# List of partition maps for a device
		partitions_list = []
		if device in self.owner.hosts[host].keys():
			partitions_list = self.owner.hosts[host][device]
		
		partition_detail_map = {}
		partition_detail_map['mountpoint'] = mountpoint
		partition_detail_map['size'] = size
		partition_detail_map['type'] = fstype
		partition_detail_map['options'] = options
		partition_detail_map['partid'] = partid

		# Append partition info to the map
		partitions_list.append(partition_detail_map)
		self.owner.hosts[host][device] = partitions_list

	def run(self, args):
		filename, = args

		self.appliances = self.getApplianceNames()

		reader = stack.csv.reader(open(filename, 'rU'))
		header = None

		name = None
		type_dict = {}

		rowid = 1
		line = 0
		for row in reader:
			line += 1

			if not header:
				header = row

				#
				# make checking the header easier
				#
				required = ['name', 'device', 'size' ]

				for i in range(0, len(row)):
					if header[i] in required:
						required.remove(header[i])

				if len(required) > 0:
					msg = 'the following required fields are not present in the input file: "%s"' % ', '.join(required)	
					raise CommandError(self.owner, msg)

				continue

			rowid += 1

			device = None
			mountpoint = ''
			size = None
			type = ''
			options = None
			partid = None

			for i in range(0, len(row)):
				field = row[i]
				if not field:
					continue

				if header[i] == 'name':
					name = field.lower()

					#
					# every time the name changes, reset
					# the rowid
					#
					rowid = 1

				elif header[i] == 'device':
					device = field.lower()

				elif header[i] == 'mountpoint':
					mountpoint = field.lower()

				elif header[i] == 'size':
					try:
						size = int(field)
						if size < 0:
							msg = 'size "%d" must be 0 or greater' % size
							raise CommandError(self.owner, msg)
					except:
						if field.lower() == 'recommended':
							size = -1
						elif field.lower() == 'hibernation':
							size =  -2
						else:
							msg = 'size "%s" must be an integer' % field
							raise CommandError(self.owner, msg)
				elif header[i] == 'type':
					type = field.lower()
				elif header[i] == 'options':
					options = field
				elif header[i] == 'partid':
					try:
						partid = int(field)
						if partid < 1:
							msg = 'partid "%d" must be 1 or greater' % partid
							raise CommandError(self.owner, msg)
					except:
						pass

			#
			# the first non-header line must have a host name
			#
			if line == 1 and not name:
				msg = 'empty host name found in "name" column'
				raise CommandError(self.owner, msg)

			if name in self.appliances or name == 'global':
				hosts = [ name ]
			else:
				hosts = self.getHostnames([ name ])

			if not hosts:
				msg = '"%s" is not host nor is it an appliance in the database' % name
				raise CommandError(self.owner, msg)

			if not partid:
				partid = rowid

			for host in hosts:
				self.doit(host, device, partid, mountpoint, 
					size, type, options, line)
				#
				# Create type_dict with the {fstype : mountpoints}
				#  to validate lvm definitions.
				# E.g. {'node204-volgroup': ['volgrp01'], 
				#       'node204-lvm': ['pv.01', 'pv.02', 'pv.03']} 
				#
				device_arr = []
				type_key = host + '-' + type
				if type_key not in type_dict:
					device_arr = []
				else:
					device_arr = type_dict[type_key]
				device_arr.append(mountpoint)
				type_dict[type_key] = device_arr

		# Regexp to match Hard disk labels
		hd_label_regexp = '(xvd[a-z]+)|([shv]d[a-z]+)|(md[0-9]+)'
		hd_regexp = re.compile(hd_label_regexp)

		# Revalidate the spreadsheet to check if pv's, volgroups have been defined
		for host in hosts:
			# Get device map for a host
			device_map = self.owner.hosts[host]
			for d in device_map.keys():
				d_map = device_map[d][0]
				# Check if volgroups have an already defined physical volume	
				if d_map['type'] == 'volgroup':
					device_arr = d.split(' ')
					for da in device_arr:
						#
						# If pv's have not been defined before 
						# then throw an error
						#
						if da not in type_dict[host + '-lvm']: 
							msg = 'pv "%s" not defined' % da
							raise CommandError(self.owner, msg)
				elif not hd_regexp.match(d):
					if d not in type_dict[host + '-volgroup']:
						msg = 'unrecgonized block device label or undefined volgroup "%s"' % d
						raise CommandError(self.owner, msg)
					else:
						# If its a volgroup, a --name option is required
						try:
							name_opt = d_map['options'].index("--name=")
						except:
							msg = 'Volgroup "%s" for host "%s" ' + \
								'needs "--name=<volname>" ' + \
								'in the OPTIONS field'
							raise CommandError(self.owner, msg % (d, host))


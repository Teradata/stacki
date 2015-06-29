# @SI_Copyright@
#                             www.stacki.com
#                                  v1.0
# 
#      Copyright (c) 2006 - 2015 StackIQ Inc. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
# 
# 	 "This product includes software developed by StackIQ" 
#  
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY STACKIQ AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@

import csv
import re
import sys
import stack.commands

class Implementation(stack.commands.ApplianceArgumentProcessor,
	stack.commands.HostArgumentProcessor,
	stack.commands.NetworkArgumentProcessor,
	stack.commands.Implementation):	

	"""
	Put storage partition configuration into the database based on
	a comma-separated formatted file.
	"""

	def doit(self, host, device, mountpoint, size, type):
		#
		# error checking
		#
		if device == None:
			msg = 'empty value found for "device" column at line %d' % line
			sys.exit((-1, msg, ''))
		if mountpoint == None:
			msg = 'empty value found for "mountpoint" column at line %d' % line
			sys.exit((-1, msg, ''))
		if size == None:
			msg = 'empty value found for "size" column at line %d' % line
			sys.exit((-1, msg, ''))

		if type == None:
			msg = 'empty value found for "type" column at line %d' % line
		if host not in self.owner.hosts.keys():
			self.owner.hosts[host] = {}
		
		# List of partition maps for a device
		partitions_list = []
		if device in self.owner.hosts[host].keys():
			partitions_list = self.owner.hosts[host][device]
		
		partition_detail_map = {}
		partition_detail_map['mountpoint'] = mountpoint
		partition_detail_map['size'] = size
		partition_detail_map['type'] = type
		# Append partition info to the map
		partitions_list.append(partition_detail_map)
		self.owner.hosts[host][device] = partitions_list

	def run(self, args):
		filename, = args

		self.appliances = self.getApplianceNames()

		reader = csv.reader(open(filename, 'rU'))
		header = None
		line = 0

		name = None

		for row in reader:
			line += 1

                        # Ignore empty rows in the csv which happens
                        # frequently with excel
                        
                        empty = True
                        for cell in row:
                                if cell.strip():
                                        empty = False
                        if empty:
                                continue

			if not header:
				header = row

				#
				# make checking the header easier
				#
				required = ['name', 'device', 'mountpoint',
					'size', 'type']

				for i in range(0, len(row)):
					header[i] = header[i].strip().lower()

					if header[i] in required:
						required.remove(header[i])

				if len(required) > 0:
					msg = 'the following required fields are not present in the input file: "%s"' % ', '.join(required)	
					sys.exit((-1, msg, ''))

				continue
			
			device = None
			mountpoint = None
			size = None
			type = None

			for i in range(0, len(row)):
				field = row[i].strip()
				if not field:
					continue

				if header[i] == 'name':
					name = field.lower()

				elif header[i] == 'device':
					device = field.lower()

				elif header[i] == 'mountpoint':
					mountpoint = field.lower()

				elif header[i] == 'size':
					try:
						size = int(field)
					except:
						msg = 'size "%s" must be an integer' % field
						sys.exit((-1, msg, ''))

					if size < 0:
						msg = 'size "%d" must be 0 or greater' % size
						sys.exit((-1, msg, ''))

				elif header[i] == 'type':
					type = field.lower()
	
			#
			# the first non-header line must have a host name
			#
			if line == 1 and not name:
				msg = 'empty host name found in "name" column'
				sys.exit((-1, msg, ''))

			if name in self.appliances or name == 'global':
				hosts = [ name ]
			else:
				hosts = self.getHostnames([ name ])

			if not hosts:
				msg = '"%s" is not host nor is it an appliance in the database' % name
				sys.exit((-1, msg, ''))

			for host in hosts:
				self.doit(host, device, mountpoint, size, type)

# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@


import re
import sys
import stack.csv
import stack.commands
from stack.exception import *

class Implementation(stack.commands.ApplianceArgumentProcessor,
	stack.commands.HostArgumentProcessor, stack.commands.Implementation):	

	"""
	Unload (remove) hosts from the database based on comma-separated
	formatted file.
	"""

	def run(self, args):
		filename, = args

		hosts = self.getHostnames()

		reader = stack.csv.reader(open(filename, 'rU'))
		header = None
		dict   = {}
		for row in reader:
			if not header:
				header = row

				#
				# make checking the header easier
				#
				required = [ 'name' ] 

				for i in range(0, len(row)):
					if header[i] in required:
						required.remove(header[i])

				if len(required) > 0:
					raise CommandError(self.owner, 'csv file is missing column(s) "%s"' % ', '.join(required))

				continue

			for i in range(0, len(row)):
				field = row[i]

				if header[i] == 'name' and field in hosts:
					dict[field] = True


		for host in dict.keys():
			self.owner.call('remove.host', [ host ])
		self.owner.call('sync.config')
		self.owner.call('sync.host.config')


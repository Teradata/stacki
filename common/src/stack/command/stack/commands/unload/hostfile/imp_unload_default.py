# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


import stack.csv
import stack.commands
from stack.commands import ApplianceArgProcessor, HostArgProcessor
from stack.exception import CommandError

class Implementation(ApplianceArgProcessor, HostArgProcessor, stack.commands.Implementation):

	"""
	Unload (remove) hosts from the database based on comma-separated
	formatted file.
	"""

	def run(self, args):
		filename, = args

		hosts = self.getHostnames()

		try:
			reader = stack.csv.reader(open(filename, encoding='ascii'))
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
		except UnicodeDecodeError:
			raise CommandError(self.owner, 'non-ascii character in file')

		for host in dict.keys():
			self.owner.call('remove.host', [ host ])
		self.owner.call('sync.config')
		self.owner.call('sync.host.config')


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
	Load switch into the database based on comma-separated formatted
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
				required = [ 'name', 'model',  'ip', 'mac', 
					'interface', 'rack', 'rank', 'network']

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
			model		= None
			ip		= None
			mac		= None
			interface	= None
			rack		= None
			rank		= None
			network		= None
			username	= None
			password	= None

			# Set the appropriate variables
			for i in range(0, len(row)):
				field = row[i]
				if not field:
					continue

				if header[i] == 'name':
					name = field.lower()
				if header[i] == 'model':
					model = field.lower()
				if header[i] == 'ip':
					ip = field.lower()
				if header[i] == 'mac':
					mac = field.lower()
				if header[i] == 'interface':
					interface = field.lower()
				if header[i] == 'rack':
					rack = field
				if header[i] == 'rank':
					rank = field
				if header[i] == 'network':
					network = field.lower()
				if header[i] == 'username':
					username = field
				if header[i] == 'password':
					password = field

			# Check for any missing values that are required
			if not name:
				msg = 'empty switch name found in "name" column'
				raise CommandError(self.owner, msg)

			if not model:
				msg = 'empty model name found in "model" column'
				raise CommandError(self.owner, msg)

			# Assign values
			if name not in self.owner.switches.keys():
				self.owner.switches[name] = {}
				self.owner.switches[name]['switch']		= name
				self.owner.switches[name]['model']		= model
				self.owner.switches[name]['ip']			= ip
				self.owner.switches[name]['mac']		= mac
				self.owner.switches[name]['interface']		= interface
				self.owner.switches[name]['rack'] 		= rack
				self.owner.switches[name]['rank']		= rank
				self.owner.switches[name]['network']		= network
				self.owner.switches[name]['username']		= username
				self.owner.switches[name]['password']		= password

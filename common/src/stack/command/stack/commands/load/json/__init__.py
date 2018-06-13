# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands
import json
import sys

class command(stack.commands.Command):

	MustBeRoot = 0
	

class Command(command):
	"""
	Import data in json format from a 'stack export' command
	"""
	def run(self, params, args):


		with open ('export.json', 'r') as file:
			try:
				self.data = json.load(file)
			except ValueError:
				print('invalid json document')
				sys.exit(1)
			


		self.runPlugins(args)


		

RollName = "stacki"

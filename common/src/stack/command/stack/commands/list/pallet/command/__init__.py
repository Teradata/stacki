# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

from collections import defaultdict
import importlib
import os

import stack.file
import stack.commands


class Command(stack.commands.PalletArgumentProcessor,
	stack.commands.list.command):
	"""
	List the commands provided by a pallet.

	<arg optional='1' type='string' name='pallet' repeat='1'>
	List of pallets. This should be the pallet base names (e.g., base, hpc,
	kernel). If no pallets are listed, then commands for all the pallets
	are listed.
	</arg>

	<param type='string' name='version'>
	The version number of the pallets to list. If no version number is
	supplied, then all versions of a pallet will be listed.
	</param>

	<param type='string' name='release'>
	The release number of the pallet to be listed. If no release number is
	supplied, then all releases of a pallet will be listed.
	</param>

	<param type='string' name='arch'>
	The architecture of the pallet to be listed. If no architecture is
	supplied, then all architectures of a pallet will be listed.
	</param>

	<param type='string' name='os'>
	The OS of the pallet to be listed. If no OS is supplied, then all OS
	versions of a pallet will be listed.
	</param>
	
	<example cmd='list pallet command stacki'>
	Returns the the list of commands installed by the stacki pallet.
	</example>
	"""

	def run(self, params, args):
		# Get a listing of all the subdirectories in the
		# stack.commands package
		tree = stack.file.Tree(stack.commands.__path__[0])

		# Filter it to remove any blanks and __pycache__
		directories = [
			path for path in tree.getDirs()
			if path and '__pycache__' not in path and '.' not in path
		]

		# Create a mapping of pallet names to Commands
		mapping = defaultdict(list)
		for directory in sorted(directories):
			# Load our module
			modpath = 'stack.commands.%s' % '.'.join(directory.split(os.sep))

			try:
				module = importlib.import_module(modpath)
			except SyntaxError:
				continue

			# Make sure it is a Command
			if not hasattr(module, 'Command'):
				continue

			# Load the RollName if possible
			try:
				pallet_name = getattr(module, 'RollName')
			except AttributeError:
				continue

			mapping[pallet_name].append(directory.replace(os.sep, ' '))

		# Output a list of commands for the pallets requested
		self.beginOutput()

		for pallet in self.getPallets(args, params):
			if pallet.name in mapping:
				for command in mapping[pallet.name]:
					self.addOutput(pallet.name, command)
			else:
				self.addOutput(pallet.name, '')

		self.endOutput(header=['pallet', 'command'])

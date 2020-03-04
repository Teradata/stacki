# This file was originally authored by
# Brandon Davidson from the University of Oregon.
# The Rocks Developers thank Brandon for his contribution.
#
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


import pathlib
import shutil

import stack.commands
from stack.argument_processors.pallet import PalletArgumentProcessor
from stack.exception import ArgRequired

class command(PalletArgumentProcessor,
	      stack.commands.remove.command):
	pass

class Command(command):
	"""
	Remove a pallet from both the database and filesystem.

	<arg type='string' name='pallet' repeat='1'>
	List of pallets. This should be the pallet base name (e.g., base, hpc,
	kernel).
	</arg>

	<param type='string' name='version'>
	The version number of the pallet to be removed. If no version number is
	supplied, then all versions of a pallet will be removed.
	</param>

	<param type='string' name='release'>
	The release id of the pallet to be removed. If no release id is
	supplied, then all releases of a pallet will be removed.
	</param>

	<param type='string' name='arch'>
	The architecture of the pallet to be removed. If no architecture is
	supplied, then all architectures will be removed.
	</param>

	<param type='string' name='os'>
	The OS of the pallet to be removed. If no OS is
	supplied, then all OSes will be removed.
	</param>

	<param type='bool' name='run_hooks'>
	Controls whether pallets hooks are run. This defaults to True.
	</param>

	<example cmd='remove pallet kernel'>
	Remove all versions and architectures of the kernel pallet.
	</example>

	<example cmd='remove pallet ganglia version=5.0 arch=i386'>
	Remove version 5.0 of the Ganglia pallet for i386 nodes.
	</example>

	<related>add pallet</related>
	<related>enable pallet</related>
	<related>disable pallet</related>
	<related>list pallet</related>
	<related>create pallet</related>
	"""

	def run(self, params, args):
		if len(args) < 1:
			raise ArgRequired(self, 'pallet')

		run_hooks, = self.fillParams([
			('run_hooks', True),
		])

		self.beginOutput()

		regenerate = False
		for pallet in self.get_pallets(args, params):
			# Run any hooks before we regenerate the repo file and remove the pallet.
			if run_hooks:
				self.run_pallet_hooks(operation="remove", pallet_info=pallet)

			self.clean_pallet(pallet)
			regenerate = True

		# Regenerate the stacki.repo if needed
		if regenerate:
			self._exec("""
				/opt/stack/bin/stack report host repo localhost |
				/opt/stack/bin/stack report script |
				/bin/sh
			""", shell=True)

		self.endOutput(padChar='')

	def clean_pallet(self, pallet):
		"""
		Remove pallet files and database entry for this arch and OS.
		"""

		self.addOutput('',
			f'Removing {pallet.name} {pallet.version}-{pallet.rel}-'
			f'{pallet.os}-{pallet.arch} pallet ...'
		)

		# Remove the pallet files and as much as the tree as possible
		tree = [
			'/export/stack/pallets', pallet.name, pallet.version,
			pallet.rel, pallet.os, pallet.arch
		]

		# Walk up the tree to clean it up, but stop at the top directory
		while len(tree) > 1:
			path = pathlib.Path().joinpath(*tree)

			# if for some reason the directory is already partially deleted
			if not path.exists():
				tree.pop()
				continue
			# The arch is the bottom of the tree, we remove everything
			if tree[-1] == pallet.arch:
				shutil.rmtree(path)
			else:
				# Just remove the directory if possible
				try:
					path.rmdir()
				except OSError:
					# Directory wasn't empty, we are done
					break

			# Move up a level in the tree
			tree.pop()

		# Remove the pallet from the database
		self.db.execute('delete from rolls where id=%s', (pallet.id,))

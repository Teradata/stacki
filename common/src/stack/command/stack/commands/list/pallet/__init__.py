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


import stack.commands
from stack.commands import PalletArgProcessor
from stack.util import flatten

class command(stack.commands.list.command, PalletArgProcessor):
	pass

class Command(command):
	"""
	List the status of available pallets.

	<arg optional='1' type='string' name='pallet' repeat='1'>
	List of pallets. This should be the pallet base name (e.g., base, hpc,
	kernel). If no pallets are listed, then status for all the pallets are
	listed.
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

	<param type='bool' name='expanded' optional='0'>
	Displays an additional column containing the url of the pallet.
	</param>

	<example cmd='list pallet kernel'>
	List the status of the kernel pallet.
	</example>

	<example cmd='list pallet'>
	List the status of all the available pallets.
	</example>

	<example cmd='list pallet expanded=true'>
	List the status of all the available pallets and their urls.
	</example>

	<related>add pallet</related>
	<related>remove pallet</related>
	<related>enable pallet</related>
	<related>disable pallet</related>
	<related>create pallet</related>
	"""

	def run(self, params, args):
		self.beginOutput()

		expanded, = self.fillParams([ ('expanded', 'false') ])
		expanded = self.str2bool(expanded)

		for pallet in self.get_pallets(args, params):

			boxes = ' '.join(flatten(self.db.select("""
					boxes.name from stacks, boxes
					where stacks.roll=%s and stacks.box=boxes.id
					""", (pallet.id,))))

			# Constuct our data to output
			output = [
				pallet.version, pallet.rel, pallet.arch, pallet.os, boxes
			]

			if expanded:
				output.append(pallet.url)

			self.addOutput(pallet.name, output)

		header = ['name', 'version', 'release', 'arch', 'os', 'boxes']
		if expanded:
			header.append('url')

		self.endOutput(header, trimOwner=False)

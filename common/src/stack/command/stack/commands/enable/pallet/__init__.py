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
import stack.deferable
from stack.argument_processors.pallet import PalletArgProcessor
from stack.exception import ArgRequired, CommandError


class Command(PalletArgProcessor, stack.commands.enable.command):
	"""
	Enable an available pallet. The pallet must already be copied on the
	system using the command "stack add pallet".

	<arg type='string' name='pallet' repeat='1'>
	List of pallets to enable. This should be the pallet base name (e.g.,
	stacki, boss, os).
	</arg>

	<param type='string' name='version'>
	The version number of the pallet to be enabled. If no version number is
	supplied, then all versions of a pallet will be enabled.
	</param>

	<param type='string' name='release'>
	The release number of the pallet to be enabled. If no release number is
	supplied, then all releases of a pallet will be enabled.
	</param>

	<param type='string' name='arch'>
	If specified enables the pallet for the given architecture.  The default
	value is the native architecture of the host.
	</param>

	<param type='string' name='os'>
	The OS of the pallet to be enabled. If no OS is supplied, then all OS
	versions of a pallet will be enabled.
	</param>

	<param type='string' name='box'>
	The name of the box in which to enable the pallet. If no
	box is specified the pallet is enabled for the default box.
	</param>

	<param type='bool' name='run_hooks'>
	Controls whether pallets hooks are run. This defaults to True.
	</param>

	<example cmd='enable pallet kernel'>
	Enable the kernel pallet.
	</example>

	<example cmd='enable pallet ganglia version=5.0 arch=i386'>
	Enable version 5.0 the Ganglia pallet for i386 nodes.
	</example>

	<related>add pallet</related>
	<related>remove pallet</related>
	<related>disable pallet</related>
	<related>list pallet</related>
	<related>create pallet</related>
	"""

	@stack.deferable.rewrite_frontend_repo_file
	def run(self, params, args):
		if len(args) < 1:
			raise ArgRequired(self, 'pallet')

		arch, box, run_hooks = self.fillParams([
			('arch', self.arch),
			('box', 'default'),
			('run_hooks', True),
		])

		# We need to write the default arch back to the params list
		params['arch'] = arch

		# Make sure our box exists
		rows = self.db.select("""
			boxes.id, oses.name from boxes, oses
			where boxes.name=%s and boxes.os=oses.id
		""", (box,))

		if len(rows) == 0:
			raise CommandError(self, 'unknown box "%s"' % box)

		# Remember the box info to simplify queries down below
		box_id, box_os = rows[0]

		pallets = self.get_pallets(args, params)
		for pallet in pallets:
			# Make sure this pallet's OS is valid for the box
			if box_os != pallet.os:
				raise CommandError(self,
					f'incompatible pallet "{pallet.name}" with OS "{pallet.os}"'
				)

			# If this pallet isn't already in the box, add it
			if self.db.count(
				'(*) from stacks where stacks.box=%s and stacks.roll=%s',
				(box_id, pallet.id)
			) == 0:
				self.db.execute(
					'insert into stacks(box, roll) values (%s, %s)',
					(box_id, pallet.id)
				)

		# Now that the repo info is regenerated, run any hooks.
		if run_hooks:
			for pallet in pallets:
				self.run_pallet_hooks(operation="enable", pallet_info=pallet)

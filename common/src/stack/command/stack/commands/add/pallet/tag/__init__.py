# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Command(stack.commands.add.pallet.command):
	"""
	Adds a tag to one or more pallets if it does not
	already exists.

	<arg type='string' name='pallet' repeat='1'>
	Name of one or more pallets.
	</arg>

	<param type='string' name='tag' optional='0'>
	Name of the tag
	</param>

	<param type='string' name='value' optional='0'>
	Value of the attribute
	</param>

	<param type='string' name='version'>
	Version of the pallet
	</param>

	<param type='string' name='release'>
	Release of the pallet
	</param>

	<param type='string' name='arch'>
	Arch of the pallet
	</param>

	<param type='string' name='os'>
	OS of the pallet
	</param>
	"""

	def run(self, params, args):
		self.command('set.pallet.tag', self._argv + [ 'force=no' ])
		return self.rc


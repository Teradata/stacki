# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import fnmatch
import stack.commands
from stack.commands import PalletArgProcessor

class Command(stack.commands.list.command, PalletArgProcessor):
	"""
	Lists the set of tags for hosts.

	<arg optional='1' type='string' name='pallet' repeat='1'>
	Name of the pallet. If no pallet is specified tags are listed
	for all pallets.
	</arg>

	<param type='string' name='tag' optional='0'>
	A shell syntax glob pattern to specify to tags to
	be listed.
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

		pallets = self.get_pallets(args, params)

		(glob, ) = self.fillParams([
			('tag', '*')
			])

		tags = {}
		for (tname, tvalue, pid) in self.db.select("""
			t.tag, t.value, p.id from
			rolls p, tags t where
			t.scope   = "pallet" and
			t.scopeid = p.id
			"""):
			if pid not in tags:
				tags[pid] = {}
			if fnmatch.fnmatch(tname, glob):
				tags[pid][tname] = tvalue

		self.beginOutput()

		for pallet in pallets:
			if pallet.id not in tags:
				continue
			for key in sorted(tags[pallet.id].keys()):
				value = tags[pallet.id][key]
				self.addOutput(pallet.name,
					       (pallet.version, pallet.rel,
						pallet.arch, pallet.os,
					        key, value))

		self.endOutput(('pallet', 'version', 'release', 'arch', 'os',
				'tag', 'value'))






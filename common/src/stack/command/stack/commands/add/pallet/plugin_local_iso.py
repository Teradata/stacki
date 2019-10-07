#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import pathlib
import stack.commands

class Plugin(stack.commands.Plugin):
	def provides(self):
		return 'local_iso'

	def run(self, args):
		'''
		Iterate through args, and if arg is an iso already on the filesystem,
		mount it in the provided temporary directory

		args is a dictionary
		{
			arg_X: {
				canonical_arg: full_path_to_arg,
				exploded_path: tempdir
				},
		}
		returns a dictionary with the same format, but only for args that matched.
		'''

		# strategy:
		# check if iso
		# verify iso exists
		# mount iso to tempdir
		# return matches

		matches = {}
		for arg in args:
			p = pathlib.Path(args[arg]['canonical_arg'])
			if p.is_file() and p.suffix == '.iso':
				self.owner.mount(str(p), args[arg]['exploded_path'])
				matches[arg] = args[arg]

		return matches

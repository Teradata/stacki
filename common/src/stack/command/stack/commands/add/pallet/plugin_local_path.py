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
		return 'local_path'

	def run(self, args):
		"""
		find a pallet where the path is already on the frontend

		Iterate through args, and if arg is a path, just use that

		args is a dictionary
		{
			arg_X: {
				canonical_arg: full_path_to_arg,
				exploded_path: tempdir
				},
		}
		"""

		for arg in args:
			p = pathlib.Path(args[arg]['canonical_arg'])
			if p.is_dir():
				# ignore the tempdir, no sense in re-mounting or copying.
				args[arg]['exploded_path'] = args[arg]['canonical_arg']

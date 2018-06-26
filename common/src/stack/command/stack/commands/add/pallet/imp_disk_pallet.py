#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import stack.commands
import subprocess
import tempfile
import shutil
import os
from urllib.parse import urlparse
import stack.file
from stack.exception import CommandError


class Implementation(stack.commands.Implementation):
	"""
	Add a pallet from a directory on disk.
	Really a re-add since the files are not copied.
	"""

	def run(self, args):
		(clean, prefix, loc, updatedb) = args

		name    = next(reversed(loc.split(os.sep)))
		version = os.listdir(loc)[0]
		release = os.listdir(os.path.join(loc, version))[0]
		osname  = os.listdir(os.path.join(loc, version, release))[0]
		arch    = os.listdir(os.path.join(loc, version, release, osname))[0]

		if self.owner.dryrun:
			self.owner.addOutput(name, [version, release, arch, osname, loc])
		if updatedb:
			self.owner.insert(name, version, release, arch, osname, loc)

RollName = "stacki"

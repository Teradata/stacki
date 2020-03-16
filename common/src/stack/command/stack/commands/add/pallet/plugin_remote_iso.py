#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import pathlib
import tempfile
import urllib.parse

import stack.commands
from stack.exception import CommandError
from stack.download import fetch, FetchError

class Plugin(stack.commands.Plugin):
	def provides(self):
		return 'remote_iso'

	def run(self, args):
		'''
		Iterate through args, and if arg is an iso on a remote filesystem,
		fetch it, save it to tempdirY, and mount it in another tempdirZ.

		Adds callbacks to delete tempdirY/arg and unmount tempdirZ

		args is a dictionary
		{
			arg_X: {
				canonical_arg: full_path_to_arg,
				exploded_path: tempdir
				},
		}
		'''

		# strategy:
		# check if remote path
		# check if iso
		# fetch iso and save to temporary location on local filesystem
		# mount iso to tempdir

		for arg in args:
			canon_arg = args[arg]['canonical_arg']
			tempdir = args[arg]['exploded_path']

			if not canon_arg.startswith(('https://', 'http://', 'ftp://')):
				continue
			if not canon_arg.endswith('.iso'):
				continue

			try:
				remote_filename = pathlib.Path(urllib.parse.urlparse(canon_arg).path).name
				# passing True will display a % progress indicator in stdout
				local_path = fetch(canon_arg, self.owner.username, self.owner.password, False, f'{tempdir}/{remote_filename}')
			except FetchError as e:
				raise CommandError(self, e)

			# make a second tempdir to actually mount the iso in.
			# this is what we will return to add pallet
			tmp_mnt_dir = tempfile.mkdtemp()

			fi = pathlib.Path(local_path)
			if not fi.is_file():
				raise CommandError(self, f'Error fetching {fi}: not recognized as an iso file')

			try:
				self.owner.mount(local_path, tmp_mnt_dir)
			except CommandError:
				# mount can fail and that's fine, but we want to clean up if it does
				raise
			finally:
				# cleanup the downloaded iso junk
				# NOTE: cleanups happen in reverse order of insertion
				# due to the ordering explicitly call umount, so it happens before the iso unlink
				self.owner.deferred.callback(pathlib.Path(tmp_mnt_dir).rmdir)
				self.owner.deferred.callback(pathlib.Path(f'{local_path}').unlink)
				self.owner.deferred.callback(self.owner.umount, local_path, tmp_mnt_dir)

			args[arg]['exploded_path'] = tmp_mnt_dir

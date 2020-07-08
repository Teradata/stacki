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
import subprocess

import stack.commands
from stack.exception import CommandError

class Plugin(stack.commands.Plugin):
	def provides(self):
		return 'remote_path'

	def run(self, args):
		'''
		Iterate through args, and if arg is a URL to a remote filesystem,
		recursively fetch it, save it to tempdir

		args is a dictionary
		{
			arg_X: {
				canonical_arg: full_path_to_arg,
				exploded_path: tempdir
				},
		}
		'''

		for arg in args:
			canon_arg = args[arg]['canonical_arg']
			tempdir = args[arg]['exploded_path']

			if not canon_arg.startswith(('https://', 'http://', 'ftp://')):
				continue
			if canon_arg.endswith('.iso'):
				continue

			creds = []
			if self.owner.username and self.owner.password:
				creds = [
					'--user={self.owner.username}',
					'--password={self.owner.password}',
				]

			parsed_url = urllib.parse.urlparse(canon_arg)
			path = pathlib.Path(parsed_url.path).resolve()
			cut_dirs = len(path.parts) - 1
			norm_loc = f'{parsed_url.scheme}://{parsed_url.netloc}{path}'
			wget_cmd = [
				'wget',
				*creds,
				'--recursive', # recursive download
				'--no-host-directories', # Don't create host directory
				'--no-parent',  # Don't create parent directories
				'--mirror', # mirror
				f'--cut-dirs={cut_dirs}',
				'--reject=TBL,index.html*',
				f'--directory-prefix={tempdir}', # directory to save files to
				norm_loc,
			]

			try:
				result = self.owner._exec(wget_cmd, stderr=subprocess.STDOUT, check=True)
			except subprocess.CalledProcessError as e:
				raise CommandError(self, f'remote fetch failed, tried:\n{" ".join(wget_cmd)}\n{e.stdout}')

			args[arg]['exploded_path'] = tempdir

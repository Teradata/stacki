#
# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import stack.commands
import subprocess
import tempfile
import shutil
import sys
import os
from urllib.parse import urlparse
import stack.file
from stack.exception import CommandError


class Implementation(stack.commands.Implementation):
	"""
	Download and add network pallets. A requirement
	is that pallets have to have the roll-<pallet>.xml
	file at the root of the directory. If not, then
	the command will raise an exception
	"""

	def run(self, args):
		(clean, prefix, loc, updatedb) = args

		tempdir = tempfile.mkdtemp()
		cwd = os.getcwd()
		os.chdir(tempdir)
		wget_cmd = ['wget', '-nv',
			'-r', # recursive download
			'-l', '1', # 1st level directory
			'-nd',	# Don't create directories
			'-np',	# Don't create parent directories
			'-A', 'roll-*.xml', # Only download roll-*.xml files
			loc]
		print(' '.join(wget_cmd))
		s = subprocess.Popen(wget_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		rc = s.wait()
		o, e = s.communicate()
		if rc:
			os.chdir(cwd)
			shutil.rmtree(tempdir)
			raise CommandError(self, e.strip())
		if len(os.listdir('.')) > 1:
			os.chdir(cwd)
			shutil.rmtree(tempdir)
			raise CommandError(self, 'Please specify URL for a single pallet')

		xmlfile = os.listdir('.')[0].strip()

		pallet = stack.file.RollInfoFile(xmlfile)
		name = pallet.getRollName()
		vers = pallet.getRollVersion()
		release = pallet.getRollRelease()
		arch = pallet.getRollArch()
		OS = pallet.getRollOS()

		destdir = os.path.join(prefix, name, vers, release, OS, arch)
		if os.path.exists(destdir) and \
			os.path.isdir(destdir):
			shutil.rmtree(destdir)
		os.makedirs(destdir)

		
		p = urlparse.urlparse(loc)
		path = os.path.normpath(p.path)
		cut_dirs = len(path.split(os.sep)) - 1
		# Normalize URL. Otherwise cutdirs behaves inconsistently
		norm_loc = "%s://%s%s/" % (p.scheme, p.netloc, path)
		wget_cmd = ['wget', '-q',
			'-r', # recursive download
			'-nH', # Don't create host directory
			'-np',	# Don't create parent directories
			'-m', # mirror
			'--cut-dirs=%d' % cut_dirs, 
			'--reject=TBL,index.html*',
			'-P', destdir, # directory to save files to
			norm_loc ]

		print(' '.join(wget_cmd))

		s = subprocess.Popen(wget_cmd, stdout=sys.stdout, stderr=sys.stdout)
		rc = s.wait()
		os.chdir(cwd)
		shutil.rmtree(tempdir)

		if updatedb:
			self.owner.insert(name, vers, release, arch, OS)

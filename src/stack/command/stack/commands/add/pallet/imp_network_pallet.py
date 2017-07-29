#
# @SI_Copyright@
#                               stacki.com
#                                  v4.0
# 
#      Copyright (c) 2006 - 2017 StackIQ Inc. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
# 
# 	 "This product includes software developed by StackIQ" 
#  
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY STACKIQ AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL STACKIQ OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@
#

import stack.commands
import subprocess
import tempfile
import shutil
import sys
import os
from urllib.parse import urlparse
import stack.file
from stack.exception import *

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
			'-l','1', # 1st level directory
			'-nd',	# Don't create directories
			'-np',	# Don't create parent directories
			'-A','roll-*.xml', # Only download roll-*.xml files
			loc]
		print (' '.join(wget_cmd))
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
			'-P',destdir, # directory to save files to
			norm_loc ]

		print (' '.join(wget_cmd))

		s = subprocess.Popen(wget_cmd, stdout=sys.stdout, stderr=sys.stdout)
		rc = s.wait()
		os.chdir(cwd)
		shutil.rmtree(tempdir)

		if updatedb:
			self.owner.insert(name, vers, release, arch, OS)

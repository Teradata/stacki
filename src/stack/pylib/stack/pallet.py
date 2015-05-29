# @SI_Copyright@
#                             www.stacki.com
#                                  v1.0
# 
#      Copyright (c) 2006 - 2015 StackIQ Inc. All rights reserved.
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
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@
#
# @Copyright@
#  				Rocks(r)
#  		         www.rocksclusters.org
#  		         version 5.4 (Maverick)
#  
# Copyright (c) 2000 - 2010 The Regents of the University of California.
# All rights reserved.	
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
# 	"This product includes software developed by the Rocks(r)
# 	Cluster Group at the San Diego Supercomputer Center at the
# 	University of California, San Diego and its contributors."
# 
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.  The name of the
# software includes the following terms, and any derivatives thereof:
# "Rocks", "Rocks Clusters", and "Avalanche Installer".  For licensing of 
# the associated name, interested parties should contact Technology 
# Transfer & Intellectual Property Services, University of California, 
# San Diego, 9500 Gilman Drive, Mail Code 0910, La Jolla, CA 92093-0910, 
# Ph: (858) 534-5815, FAX: (858) 534-7345, E-MAIL:invent@ucsd.edu
#  
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @Copyright@

import os
import stack.media

class GetPallet:
	def __init__(self):
		#
		# in a default installation, make sure /export points to a
		# partition *not* on the '/' partition
		#
		self.anaconda = None
		self.media = stack.media.Media()

		cwd = os.getcwd()
		os.chdir('/mnt/sysimage')
		try:
			os.symlink('state/partition1', 'export')
		except:
			pass
		os.chdir(cwd)

	def checkDVD(self, diskname):
		#
		# check that it is the right pallet CD
		#
		found_disk = 'false'
		while found_disk == 'false':
			diskid = self.media.getId()

			if diskname == diskid:
				found_disk = 'true'

			if found_disk == 'false':
				self.media.ejectCD()

				if 0:
					self.anaconda.intf.messageWindow(_("Install Pallet"),
						_("Put Pallet disk")
						+ " '%s' " % (diskname)
						+ _("in the drive\n"))
				else:
					print 'Put Pallet disk %s in drive' \
						% diskname

	def downloadDVDPallets(self, pallets):
		diskids = []
		for pallet in pallets:
			(name, version, arch, url, diskid) = pallet

			if diskid != '' and diskid not in diskids:
				diskids.append(diskid)

		diskids.sort()
		for d in diskids:
			#
			# ask the user to put the right media in the bay
			#
			self.checkDVD(d)

			#
			# for DVDs, we can't download individual pallets --
			# we get all of them off the DVD
			#
			basePalletDir = '/mnt/sysimage/export/stack/pallets'

			cmd = '/opt/stack/bin/stack add pallet '
			cmd += 'updatedb=n dir=%s' % basePalletDir
			os.system(cmd)

		if self.media.mounted():
			self.media.ejectCD()

	def downloadNetworkPallets(self, pallets):
		for pallet in pallets:
			(name, version, arch, url, diskid) = pallet

			if diskid != '':
				continue

			path = os.path.join(name, version, 'redhat', arch)
			url = os.path.join(url, path)
			cutdirs = len(url.split(os.sep)) - 3
			localpath = os.path.join(
				'/mnt/sysimage/export/stack/pallets/', path)

			os.system('mkdir -p %s' % localpath)
			os.chdir(localpath)

			flags = '-m -np -nH --dns-timeout=3 '
			flags += '--connect-timeout=3 '
			flags += '--read-timeout=10 --tries=3'
			cmd = '/usr/bin/wget %s --cut-dirs=%d %s' % (flags,
				cutdirs, url)
			os.system(cmd)

			if 0:
				w.pop()


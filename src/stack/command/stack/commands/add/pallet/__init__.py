# @SI_Copyright@
#                             www.stacki.com
#                                  v3.1
# 
#      Copyright (c) 2006 - 2016 StackIQ Inc. All rights reserved.
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

from __future__ import print_function
import os
import sys
import string
import popen2
import stack.file
import stack.commands
from stack.exception import *


class Command(stack.commands.add.command):
	"""
	Add pallet ISO images to this machine's pallet directory. This command
	copies all files in the ISOs to the local machine. The default location
	is a directory under /export/stack/pallets.

	<arg optional='1' type='string' name='pallet' repeat='1'>
	A list of pallet ISO images to add to the local machine. If no list is
	supplied, then if a pallet is mounted on /mnt/cdrom, it will be copied
	to the local machine.
	</arg>
		
	<param type='bool' name='clean'>
	If set, then remove all files from any existing pallets of the same
	name, version, and architecture before copying the contents of the
	pallets onto the local disk.  This parameter should not be set
	when adding multi-CD pallets such as the OS pallet, but should be set
	when adding single pallet CDs such as the Grid pallet.
	</param>

	<param type='string' name='dir'>
	The base directory to copy the pallet to.
	The default is: /export/stack/pallets.
	</param>

	<param type='string' name='updatedb'>
	Add the pallet info to the cluster database.
	The default is: true.
	</param>
	
	<example cmd='add pallet clean=1 kernel*iso'>
	Adds the Kernel pallet to local pallet directory.  Before the pallet is
	added the old Kernel pallet packages are removed from the pallet
	directory.
	</example>
	
	<example cmd='add pallet kernel*iso pvfs2*iso ganglia*iso'>
	Added the Kernel, PVFS, and Ganglia pallets to the local pallet
	directory.
	</example>

	<related>remove pallet</related>
	<related>enable pallet</related>
	<related>disable pallet</related>
	<related>list pallet</related>
	<related>create pallet</related>
	"""

	def copy(self, clean, prefix, updatedb):
		"""Copy all the pallets from the CD to Disk"""

		# Populate the info hash. This hash contains pallet
		# information about all the pallets present on disc.

		r, w = popen2.popen2('find %s -type f -name roll-\*.xml' %
				     self.mountPoint)
		dict = {}
		for filename in r.readlines():
			roll = stack.file.RollInfoFile(filename.strip())
			dict[roll.getRollName()] = roll
			
		if len(dict) == 0:
			
			# If the roll_info hash is empty, that means there are
			# no Rocks recognizable rolls on the Disc. This mean
			# it may just be a normal OS CD like CentOS, RHEL,
			# Scientific Linux or Solaris. In any case it's a
			# foreign CD, and should be treated as such.
			#
			# Check the OS of the CD. This is pretty easily
			# discernable. A .treeinfo file in the root of the CD
			# implies an RHEL based disc, and a .cdtoc file in the
			# root of the CD implies a Solaris 10 disc.

			treeinfo = os.path.join(self.mountPoint, '.treeinfo')
			diskinfo = os.path.join(self.mountPoint, './.disk/info')
			cdtoc    = os.path.join(self.mountPoint, '.cdtoc')
			
			if os.path.exists(treeinfo):
				res = self.runImplementation('foreign_redhat',
						       (clean, prefix,
							treeinfo))
				if res and updatedb:
					self.insert(res[0], res[1], '', res[2],
						    'redhat')
			elif os.path.exists(diskinfo):
				res = self.runImplementation('foreign_ubuntu',
						       (clean, prefix,
							diskinfo))
				if res and updatedb:
					self.insert(res[0], res[1], res[3],
						    res[2], 'ubuntu')
			else:
                                raise CommandError(self, 'unknown os on media')

		#
		# Keep going even if a foreign pallet.  Safe to loop over an
		# empty list.
		#
 		# For all pallets present, copy into the pallets directory.
		
		for key, info in dict.items():
			self.runImplementation('native_%s' % info.getRollOS(),
					       (clean, prefix, info))
			if updatedb:
				self.insert(info.getRollName(),
					info.getRollVersion(),
                                        info.getRollRelease(),
					info.getRollArch(),
					info.getRollOS())


	def insert(self, name, version, release, arch, OS):
		"""
		Insert the pallet information into the database if
		not already present.
		"""

                rows = self.db.execute("""
                       	select * from rolls where
                        name='%s' and version='%s' and rel='%s' and arch='%s' and os='%s'
                        """ % (name, version, release, arch, OS))
		if not rows:
			self.db.execute("""insert into rolls
				(name, version, rel, arch, os) values
				('%s', '%s', '%s', '%s', '%s')
				""" % (name, version, release, arch, OS))


	def run(self, params, args):
		(clean, dir, updatedb) = self.fillParams([
                        ('clean', 'n'),
			('dir', '/export/stack/pallets'),
			('updatedb', 'y')
                        ])

		clean = self.str2bool(clean)
		updatedb = self.str2bool(updatedb)

		self.mountPoint = '/mnt/cdrom'
		if self.os == 'sunos':
			self.mountPoint = '/cdrom'
		if not os.path.exists(self.mountPoint):
			os.makedirs(self.mountPoint)

		# Get a list of all the iso files mentioned in
		# the command line. Make sure we get the complete 
		# path for each file.
			
		list = []
		for arg in args:
			arg = os.path.join(os.getcwd(), arg)
			if os.path.exists(arg) and arg.endswith('.iso'):
				list.append(arg)
			else:
				print("Cannot find %s or %s "\
					"is not and ISO image" % (arg, arg))
		
		for iso in list:	# have a set of iso files
			self.runImplementation('mount_%s' % self.os, iso)
			self.copy(clean, dir, updatedb)
			self.runImplementation('umount_%s' % self.os)
			
		if not list:		# no files specified look for a cdrom
			if self.runImplementation('mounted_%s' % self.os):
				self.copy(clean, dir, updatedb)
			else:
                                raise CommandError(self, 'CDROM not mounted')

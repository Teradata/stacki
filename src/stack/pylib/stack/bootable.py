#! /opt/stack/bin/python
# 
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
import shutil
import stack.file
import stack.api

class Bootable:

	def __init__(self, localdir, palletdir):
		self.palletdir = palletdir
		self.filetree = {}

		#
		# find all the pallets and carts associated with this host
		# (the host that is building the pallet), and build file trees
		# for each pallet/cart.
		#
		box = None
		for o in stack.api.Call('list host', [ 'host=localhost']):
			box = o['box']

		if not box:
			raise ValueError, 'could not find box for "localhost"'
			return

		self.filetree['local'] = stack.file.Tree(localdir)

		pallets = []
		for o in stack.api.Call('list pallet'):
			boxes  = o['boxes'].split()
			if box in boxes:
				pallets.append((o['name'], o['version'],
					o['arch']))

		for name, ver, arch in pallets:
			palletpath = os.path.join('/export', 'stack', 'pallets',
				name, ver, 'redhat', arch)

			self.filetree[name] = stack.file.Tree(palletpath)

		
	def applyRPM(self, rpm, root, flags=''):
		print('applyRPM', rpm.getBaseName(), root)

		dbdir = os.path.join(root, 'var', 'lib', 'rpm')

		os.makedirs(os.path.join(root, dbdir))
		reloc = os.system("rpm -q --queryformat '%{prefixes}\n' -p " +
			rpm.getFullName() + "| grep none > /dev/null")

		cmd = 'rpm -i --nomd5 --force --nodeps --ignorearch ' + \
			'--dbpath %s ' % (dbdir)
		if reloc:
			cmd = cmd + '--prefix %s %s %s' % (root, flags,
							rpm.getFullName())
		else:
			cmd = cmd + '--badreloc --relocate /=%s %s %s' \
					% (root, flags, rpm.getFullName())

		retval = os.system(cmd + ' > /dev/null 2>&1')
		shutil.rmtree(os.path.join(root, dbdir))

		if retval == 256:
			raise ValueError, "could not apply RPM %s" % \
				(rpm.getFullName())

		return retval


	def findFile(self, name):
		trees = self.filetree.keys()

		#
		# look in the local tree first
		#
		if 'local' in trees:
			tree = self.filetree['local']
			for d in tree.getDirs():
				for file in tree.getFiles(d):
					try:
						if file.getPackageName() == name:
							return file
					except:
						pass

					try:
						if file.getName() == name:
							return file
					except:
						pass
		for key in trees:
			if key == 'local':
				continue

			tree = self.filetree[key]
			for d in tree.getDirs():
				for file in tree.getFiles(d):
					try:
						if file.getPackageName() == name:
							return file
					except:
						pass

					try:
						if file.getName() == name:
							return file
					except:
						pass

		return None


	def installBootfiles(self, destination):
		import stat
		import stack

		print('Applying boot files')

		name = 'stack-images'
		RPM = self.findFile(name)
		if not RPM:
			raise ValueError, "could not find %s" % name

		self.applyRPM(RPM, destination)

		images = os.path.join(destination, 'opt', 'stack', 'images')
		isolinux = os.path.join(destination, 'isolinux')

		shutil.move(os.path.join(images, 'isolinux'), isolinux)

		#
		# vmlinuz and initrd.img
		#
		for file in os.listdir(images):
			if file.startswith('vmlinuz-'):
				shutil.move(os.path.join(images, file),
					os.path.join(isolinux, 'vmlinuz'))
			if file.startswith('initrd.img-'):
				shutil.move(os.path.join(images, file),
					os.path.join(isolinux, 'initrd.img'))

		if stack.release == '7.x':
			imagesdir = os.path.join(destination, 'images')
		else:
			imagesdir = os.path.join(self.palletdir, 'images')

		if not os.path.exists(imagesdir):
			os.makedirs(imagesdir)

		if stack.release == '7.x':
			#
			# upgrade.img
			#
			fileold = os.path.join(os.path.join(images,
				'upgrade.img'))
			filenew = os.path.join(imagesdir, 'upgrade.img')
			print('fileold %s' % fileold)
			print('filenew %s' % filenew)
			shutil.copy(fileold, filenew)
		else:
			#
			# install.img
			#
			fileold = os.path.join(os.path.join(images,
				'install.img'))
			filenew = os.path.join(imagesdir, 'install.img')
			os.rename(fileold, filenew)

		os.chmod(filenew, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

		if stack.release == '7.x':
			#
			# updates.img
			#
			fileold = os.path.join(os.path.join(images,
				'updates.img'))
			filenew = os.path.join(imagesdir, 'updates.img')

			os.rename(fileold, filenew)
			os.chmod(filenew,
				stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

			#
			# squashfs.img from LiveOS
			#
			f = self.findFile('squashfs.img')
			if not f:
				raise ValueError, \
					"could not find 'squashfs.img'"

			fileold = f.getFullName()
			print('fileold %s' % f.getFullName())

			livenewdir = os.path.join(destination, 'LiveOS')
			if not os.path.exists(livenewdir):
				os.makedirs(livenewdir)

			filenew = os.path.join(livenewdir, 'squashfs.img')

			print('fileold %s' % fileold)
			print('filenew %s' % filenew)
			shutil.copy(fileold, filenew)
			os.chmod(filenew,
				stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

		#
		# put the 'barnacle' executable in the ISO
		#
		name = 'stack-barnacle'
		RPM = self.findFile(name)
		if RPM:
			self.applyRPM(RPM, destination)
			src = os.path.join(destination, 'opt', 'stack',
				'bin', 'frontend-install.py')
			dst = os.path.join(destination, 'frontend-install.py')
			os.rename(src, dst)

		#
		# clean up other image files from the stack-image RPM
		#
		shutil.rmtree(os.path.join(destination, 'opt'),
			ignore_errors = 1)
		shutil.rmtree(os.path.join(destination, 'var'),
			ignore_errors = 1)

		return


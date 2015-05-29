#! /opt/stack/bin/python
# 
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
import shutil
import tempfile
import stack.dist
import stack.file
import stack.util


class Bootable:

	def __init__(self, dist, rolldir):
		self.dist = dist
		self.rolldir = rolldir

		#
		# build a list of CPUs, from 'best' to 'worst' match
		#

		#
		# the 'native' cpu is always first
		#
		self.cpus = []
		i86cpus = [ 'i686', 'i586', 'i486', 'i386' ]

		native = os.uname()[4]
		self.cpus.append(native)

		if native in i86cpus:
			self.cpus += i86cpus

		self.cpus.append('noarch')
		return


	def getBestRPM(self, name):
		r = self.dist.getRPM(name)
		if r == None:
			return None
			
		rpm = None

		if len(r) == 1:
			rpm = r[0]
		elif len(r) > 1:
			print 'found more than one RPM for %s' % (name)

			for c in self.cpus:
				for i in r:
					if i.getPackageArch() == c:
						rpm = i
						break

				if rpm:
					print '\tusing %s' % \
							rpm.getUniqueName()
					break
			
		return rpm


	def applyRPM(self, rpm, root, flags=''):
		"""Used to 'patch' the new distribution with RPMs from the
		distribution.  We use this to always get the correct
		genhdlist, and to apply eKV to Stack distributions.
        
		Throws a ValueError if it cannot find the specified RPM, and
		BuildError if the RPM was found but could not be installed."""

#		print 'applyRPM', rpm.getBaseName(), root

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


	def patchImage(self, image_name):
		#
		# image_name = full pathname to stage2.img file
		#
		cwd = os.getcwd()

		# Create a scratch area on the local disk of the machine, we
		# don't want to do this in the distribution since it might be
		# over NFS (not a problem, just slow).
        
		tmp = tempfile.mktemp()
		os.makedirs(tmp)

		stageimg = os.path.join(tmp, 'img')	# uncompress img
		stagemnt = os.path.join(tmp, 'mnt')	# mounted image
		stagesrc = os.path.join(tmp, 'src')	# working image
		os.makedirs(stagemnt)

		# - uncompress the the 2nd stage image from the distribution
		# - mount the file on the loopback device
		#	(requires SUID 'C' code)
		# - copy all file into the working images
		# - umount the loopback device

		shutil.copy(image_name, stageimg)

		os.system('mount -oloop -t squashfs %s %s' %
			(stageimg, stagemnt))

		os.chdir(stagemnt)
		os.system('find . | cpio -pdu %s 2> /dev/null' % stagesrc)
		os.chdir(cwd)

		os.system('umount %s' % stagemnt)

		# Stamp the new image with our likeness so the new loader
		# will "verify" its authenticity. This stamp must be repeated
		# in an identical file in the initrd.

		stamp = open(os.path.join(stagesrc, ".buildstamp"), "w")
		stamp.write("Stack-RedHat\n")
		stamp.close()

		# - create a new image file based on the size of the
		#	working image
		# - mount the file on loopback
		# - copy the working image into the mounted images
		# - umount the file
		# - compress, and copy, the image back into the distribution

		print '    building CRAM filesystem ...'
		os.system('mkcramfs %s %s > /dev/null' % \
			(stagesrc, image_name))

		# Erase the evidence.
		shutil.rmtree(tmp)
		return


	def installBootfiles(self, destination):
		import stat

		print 'Applying boot files'

		name = 'stack-images'
		RPM = self.getBestRPM(name)
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

		#
		# install.img
		#
		imagesdir = os.path.join(self.rolldir, 'images')
		if not os.path.exists(imagesdir):
			os.makedirs(imagesdir)

		install = os.path.join(os.path.join(images, 'install.img'))
		image = os.path.join(imagesdir, 'install.img')
		os.rename(install, image)
		os.chmod(image, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

		#
		# put the 'barnacle' executable in the ISO
		#
		name = 'stack-barnacle'
		RPM = self.getBestRPM(name)
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


	def copyBasefiles(self, destination):
		if not os.path.exists(destination):
			os.makedirs(destination)
		basepath = os.path.join(self.dist.getPath(), 'RedHat', 'base')
		cmd = 'cp %s/* %s' % (basepath, destination)
		os.system(cmd)
		os.system('touch %s/comps.rpm' % destination)
		return


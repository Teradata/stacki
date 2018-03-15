#! /opt/stack/bin/python
# 
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import os
import shutil
import stack.file
import stack.api

class Bootable(stack.bootable.Bootable):

	def installBootfiles(self, destination):
		import stat
		import stack

		print('Applying RedHat boot files', destination)

		name = 'stack-images'
		RPM  = self.findFile(name)
		if not RPM:
			raise ValueError("could not find %s" % name)

		self.applyRPM(RPM, destination)

		images   = os.path.join(destination, 'opt', 'stack', 'images')
		isolinux = os.path.join(destination, 'isolinux')

		shutil.move(os.path.join(images, 'isolinux'), isolinux)

		#
		# vmlinuz and initrd.img
		#
		for file in os.listdir(images):
			if file.startswith('vmlinuz-'):
				shutil.move(os.path.join(images, file), os.path.join(isolinux, 'vmlinuz'))
			if file.startswith('initrd.img-'):
				shutil.move(os.path.join(images, file), os.path.join(isolinux, 'initrd.img'))

		imagesdir = os.path.join(self.palletdir, 'images')

		if not os.path.exists(imagesdir):
			os.makedirs(imagesdir)

		if stack.release == 'redhat6':
			#
			# install.img
			#
			fileold = os.path.join(os.path.join(images, 'install.img'))
			filenew = os.path.join(imagesdir, 'install.img')
			os.rename(fileold, filenew)
			os.chmod(filenew, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

		if stack.release == 'redhat7':
			#
			# updates.img
			#
			fileold = os.path.join(os.path.join(images, 'updates.img'))
			filenew = os.path.join(imagesdir, 'updates.img')

			if not os.path.exists(fileold):
				raise ValueError("cound not find '%s'" % fileold)

			os.rename(fileold, filenew)
			os.chmod(filenew, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

			#
			# squashfs.img from LiveOS
			#
			f = self.findFile('squashfs.img')
			if not f:
				raise ValueError("could not find 'squashfs.img'")

			fileold = f.getFullName()
			print('fileold %s' % f.getFullName())

			livenewdir = os.path.join(self.palletdir, 'LiveOS')
			if not os.path.exists(livenewdir):
				os.makedirs(livenewdir)

			filenew = os.path.join(livenewdir, 'squashfs.img')

			print('fileold %s' % fileold)
			print('filenew %s' % filenew)
			shutil.copy(fileold, filenew)
			os.chmod(filenew, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

		#
		# clean up other image files from the stack-image RPM
		#
		shutil.rmtree(os.path.join(destination, 'opt'), ignore_errors=1)
		shutil.rmtree(os.path.join(destination, 'var'), ignore_errors=1)



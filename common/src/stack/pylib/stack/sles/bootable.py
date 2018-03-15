#! /opt/stack/bin/python
# 
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os
import shutil
import stack.file
import stack.api


class Bootable(stack.bootable.Bootable):

	def installBootfiles(self, dstPath):

		dstISOLinuxPath = os.path.join(dstPath, 'isolinux')
		dstImagePath    = os.path.join(dstISOLinuxPath, 'image')

		srcOSPath       = self.filetree['SLES'].getRoot()

		dirs            = srcOSPath.split(os.sep)
		osVersion       = dirs[-4]
		osRelease       = dirs[-3]
		osName          = dirs[-2]
		osArch          = dirs[-1]

		
		print('Applying SLES boot files', dstPath)

		os.makedirs(dstISOLinuxPath)
		os.makedirs(dstImagePath)

		for x in os.listdir(srcOSPath):
			path = os.path.join(srcOSPath, x)
			if os.path.isdir(path) and x != 'suse':
				shutil.copytree(path, os.path.join(dstImagePath, x))
			if os.path.isfile(path) and x != 'roll-SLES.xml':
				shutil.copyfile(path, os.path.join(dstImagePath, x))


		for rpm in [ 'syslinux', 'stack-sles-images' ]:
			file  = self.findFile(rpm)
			if not file:
				raise ValueError("could not find %s" % rpm)
			self.applyRPM(file, dstPath)


		imagesPath  = os.path.join(dstPath, 'opt', 'stack', 'images')
		
		for (src, dst) in [ ( 'vmlinuz-%s-%s-%s-%s' % (osName, osVersion, osRelease, osArch), 
				      'vmlinuz' ),
				    ( 'initrd-%s-%s-%s-%s'  % (osName, osVersion, osRelease, osArch), 
				      'initrd.img' ) ]:
			try:
				shutil.copyfile(os.path.join(imagesPath, src), 
						os.path.join(dstISOLinuxPath, dst))
			except:
				print('ERROR - cannot copy %s into isolinux' % src)


		syslinuxPath = os.path.join(dstPath, 'usr', 'share', 'syslinux')
		
		for file in [ 'isolinux.bin', 'vesamenu.c32', 'chain.c32' ]:
			try:
				shutil.copyfile(os.path.join(syslinuxPath, file), 
						os.path.join(dstISOLinuxPath, file))
			except:
				print('ERROR - cannot copy %s into isolinux' % file)


		with open(os.path.join(dstISOLinuxPath, 'isolinux.cfg'), 'w') as fout:
			fout.write('default stacki\n\n')
			fout.write('label stacki\n')
			fout.write('\tkernel vmlinuz\n')
			fout.write('\tappend initrd=initrd.img autoyast=file:///tmp/profile/autoinst.xml ramdisk_size=300000 biosdevname=0 frontend install=cd:/isolinux/image\n\n')
			fout.write('label harddisk\n')
			fout.write('\tlocalboot -2\n\n')
			fout.write('implicit 1\n')
			fout.write('prompt 1\n')
			fout.write('timeout 600\n')


		for dir in [ 'opt', 'usr', 'var' ]:
			shutil.rmtree(os.path.join(dstPath, dir))


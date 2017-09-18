# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import os
import shlex
import subprocess
import stack.commands
from stack.exception import CommandError


class Implementation(stack.commands.Implementation):	
	"""
	Copy a SLES ISO to the frontend.
	"""

	name = None
	vers = None
	release = None
	arch = None

	def check_impl(self):
		if os.path.exists('/mnt/cdrom/content'):
			file = open('/mnt/cdrom/content', 'r')

			for line in file.readlines():
				l = line.split()
				if len(l) > 1:
					key = l[0].strip()
					value = l[1].strip()

					if key == 'NAME' and value == 'SUSE_SLES':
						self.name = 'SLES'
					elif key == 'VERSION':
						self.vers = value
					elif key == 'RELEASE':
						self.release = value
					elif key == 'BASEARCHS':
						self.arch = value

			if not self.release:
				self.release = stack.release
			if not self.arch:
				self.arch = 'x86_64'

			file.close()

		if self.name and self.vers:
			return True
			
		return False


	def run(self, args):
		import stack

		(clean, prefix)	 = args

		if not self.name:
			raise CommandError(self, 'unknown SLES on media')
		if not self.vers:
			raise CommandError(self, 'unknown SLES version on media')
			
		OS = 'sles'
		roll_dir = os.path.join(prefix, self.name, self.vers, OS, self.arch)
		destdir = roll_dir

		if clean and os.path.exists(roll_dir):
			print('Cleaning %s version %s ' % (self.name, self.vers), end=' ')
			print('for %s from pallets directory' % self.arch)
			os.system('/bin/rm -rf %s' % roll_dir)
			os.makedirs(roll_dir)

		print('Copying "%s" (%s,%s) pallet ...' % (self.name, self.vers, self.arch))

		if not os.path.exists(destdir):
			os.makedirs(destdir)

		cmd = 'rsync -a --exclude "TRANS.TBL" %s/ %s/' \
			% (self.owner.mountPoint, destdir)
		subprocess.call(shlex.split(cmd))


		# Copy SLES Pallet patches into the SLES pallet directory
		print("Patching SLES pallet")
		patch_dir = '/opt/stack/SLES-pallet-patches/%s/' % self.vers
		cmd = 'rsync -a %s/ %s/' % (patch_dir, destdir)
		subprocess.call(shlex.split(cmd))

		#
		# create roll-<name>.xml file
		#
		xmlfile = open('%s/roll-%s.xml' % (roll_dir, self.name), 'w')

		xmlfile.write('<roll name="%s" interface="6.0.2">\n' % self.name)
		xmlfile.write('<color edge="white" node="white"/>\n')
		xmlfile.write('<info version="%s" release="%s" arch="%s" os="%s"/>\n' % (self.vers, self.release, self.arch, OS))
		xmlfile.write('<iso maxsize="0" addcomps="0" bootable="0"/>\n')
		xmlfile.write('<rpm rolls="0" bin="1" src="0"/>\n')
		xmlfile.write('</roll>\n')

		xmlfile.close()

		return (self.name, self.vers, self.release, self.arch, OS)


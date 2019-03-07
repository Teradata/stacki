# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
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
	Copy a SLES/CaaSP ISO to the frontend.
	"""

	def check_impl(self):
		# Check the DISTRO line in the content file
		# This should be of the format
		# DISTRO	   cpe:/o:suse:sles:12:sp2,SUSE Linux Enterprise Server 12 SP2
		#
		# or:
		#
		# DISTRO	cpe:/o:suse:caasp:1.0,SUSE Container as a Service Platform 1.0

		self.name = None
		self.vers = None
		self.release = None
		self.arch = 'x86_64'

		found_distro = False
		if os.path.exists(f'{self.owner.mountPoint}/content'):
			file = open(f'{self.owner.mountPoint}/content', 'r')

			for line in file.readlines():
				l = line.split(None, 1)
				if len(l) > 1:
					key = l[0].strip()
					value = l[1].strip()

					if key == 'DISTRO':
						a = value.split(',')
						v = a[0].split(':')
						
						if v[3] == 'sles':
							self.name = 'SLES'
						elif v[3] == 'sle-sdk':
							self.name = v[3].upper()
						elif v[3] == 'ses':
							self.name = 'SUSE-Enterprise-Storage'

						if self.name:
							self.vers = v[4]
							if len(v) > 5:
								self.release = v[5]
							found_distro = True
						else:
							return False


			file.close()
		if not self.release:
			self.release = stack.release
		if found_distro:
			return True
		else:
			return False


	def run(self, args):

		(clean, prefix)	 = args

		if not self.name:
			raise CommandError(self, 'unknown SLES on media')
		if not self.vers:
			raise CommandError(self, 'unknown SLES version on media')
			
		OS = 'sles'
		roll_dir = os.path.join(prefix, self.name, self.vers, self.release, OS, self.arch)
		destdir = roll_dir

		if clean and os.path.exists(roll_dir):
			self.owner.out.write('Cleaning %s version %s ' % (self.name, self.vers))
			self.owner.out.write('for %s from pallets directory\n' % self.arch)
			if not self.owner.dryrun:
				os.system('/bin/rm -rf %s' % roll_dir)
				os.makedirs(roll_dir)

		self.owner.out.write('Copying "%s" (%s,%s) pallet ...\n' % (self.name, self.vers, self.arch))

		if not self.owner.dryrun:
			if not os.path.exists(destdir):
				os.makedirs(destdir)

			cmd = 'rsync -a --exclude "TRANS.TBL" %s/ %s/' \
				% (self.owner.mountPoint, destdir)
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

		#
		# Copy pallet patches into the respective pallet
		# directory
		#
		patch_dir = '/opt/stack/%s-pallet-patches/%s/%s' % \
			(self.name, self.vers, self.release)
		if os.path.exists(patch_dir):
			self.owner.out.write('Patching %s pallet\n' % self.name)
			if not self.owner.dryrun:
				cmd = 'rsync -a %s/ %s/' % (patch_dir, destdir)
				subprocess.call(shlex.split(cmd))


		return (self.name, self.vers, self.release, self.arch, OS, roll_dir)


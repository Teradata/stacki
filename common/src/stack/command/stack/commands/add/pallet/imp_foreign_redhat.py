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
import shlex
import subprocess
import stack.file
import stack.commands


class Implementation(stack.commands.Implementation):	
	"""
	Copy a Linux OS CD. This supports RHEL, CentOS,
	Oracle Enterprise Linux, and Scientific Linux.
	"""

	def check_impl(self):
		self.treeinfo = os.path.join(self.owner.mountPoint, '.treeinfo')
		if os.path.exists(self.treeinfo):
			return True
		return False

	def run(self, args):
		import stack

		(clean, prefix) = args

		name = None
		vers = None
		arch = None
		release = None

		file = open(self.treeinfo, 'r')
		for line in file.readlines():
			a = line.split('=')

			if len(a) != 2:
				continue

			key = a[0].strip()
			value = a[1].strip()

			if key == 'family':
				if value == 'Red Hat Enterprise Linux':
					name = 'RHEL'
				elif value.startswith('CentOS'):
					name = 'CentOS'
				elif value.startswith('Oracle'):
					name = 'OLE'
				elif value.startswith('Scientific'):
					name = 'SL'
			elif key == 'version':
				vers = value
			elif key == 'arch':
				arch = value
		file.close()

		if not name:
			name = "BaseOS"
		if not vers:
			vers = stack.version
		if not arch:
			arch = 'x86_64'
		if not release:
			release = stack.release
			
		OS = 'redhat'
		roll_dir = os.path.join(prefix, name, vers, release, OS, arch)
		destdir = roll_dir

		if clean and os.path.exists(roll_dir):
			self.owner.out.write('Cleaning %s %s-%s\n' % (name, vers, release))
			self.owner.out.write('for %s from pallets directory\n' % self.arch)

			if not self.owner.dryrun:
				os.system('/bin/rm -rf %s' % roll_dir)
				os.makedirs(roll_dir)

		self.owner.out.write('Copying %s %s-%s pallet ...\n' % (name, vers, release))

		if not self.owner.dryrun:
			if not os.path.exists(destdir):
				os.makedirs(destdir)

			cmd = 'rsync -a --exclude "TRANS.TBL" %s/ %s/' \
				% (self.owner.mountPoint, destdir)
			subprocess.call(shlex.split(cmd))

			#
			# create roll-<name>.xml file
			#
			xmlfile = open('%s/roll-%s.xml' % (roll_dir, name), 'w')

			xmlfile.write('<roll name="%s" interface="6.0.2">\n' % name)
			xmlfile.write('<color edge="white" node="white"/>\n')
			xmlfile.write('<info version="%s" release="%s" arch="%s" os="%s"/>\n' % (vers, release, arch, OS))
			xmlfile.write('<iso maxsize="0" addcomps="0" bootable="0"/>\n')
			xmlfile.write('<rpm rolls="0" bin="1" src="0"/>\n')
			xmlfile.write('</roll>\n')

			xmlfile.close()

		return (name, vers, release, arch, OS, roll_dir)

RollName = "stacki"

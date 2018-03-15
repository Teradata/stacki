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


class Bootable:

	def __init__(self, osname, localdir, palletdir):
		self.palletdir = palletdir
		self.filetree = {}

		#
		# find all the pallets and carts associated with this host
		# (the host that is building the pallet), and build file trees
		# for each pallet/cart.
		#
		box = None
		for o in stack.api.Call('list host', [ 'localhost']):
			box = o['box']

		self.filetree['local'] = stack.file.Tree(localdir)

		pallets = []
		for o in stack.api.Call('list pallet'):
			boxes  = o['boxes'].split()
			if box in boxes:
				pallets.append((o['name'], o['version'],
						o['release'], o['arch']))

		for name, ver, release, arch in pallets:
			palletpath = os.path.join('/export', 'stack', 'pallets',
						  name, ver, release, osname, arch)

			self.filetree[name] = stack.file.Tree(palletpath)

		
	def applyRPM(self, rpm, root, flags=''):
		print('applyRPM', rpm.getBaseName(), root)

		dbdir = os.path.join(root, 'var', 'lib', 'rpm')

		os.makedirs(os.path.join(root, dbdir))
		reloc = os.system("rpm -q --queryformat '%{prefixes}\n' -p " +
				  rpm.getFullName() + "| grep none > /dev/null")

		cmd = 'rpm -i --nomd5 --force --nodeps --ignorearch --dbpath %s ' % (dbdir)
		if reloc:
			cmd = cmd + '--prefix %s %s %s' % (root, flags, rpm.getFullName())
		else:
			cmd = cmd + '--badreloc --relocate /=%s %s %s' % (root, flags, rpm.getFullName())

		retval = os.system(cmd + ' > /dev/null 2>&1')
		shutil.rmtree(os.path.join(root, dbdir))

		if retval == 256:
			raise ValueError("could not apply RPM %s" % rpm.getFullName())

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
		return



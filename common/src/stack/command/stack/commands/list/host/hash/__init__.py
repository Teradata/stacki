#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import os
import hashlib
import stack.commands

class Command(stack.commands.list.host.command,
	stack.commands.BoxArgumentProcessor):
	"""
	Calculate and list the MD5 hashes of a host's:

		- pallets
		- carts
		- profile (e.g., kickstart file, autoyast file, etc.)

	<arg optional='0' type='string' name='host'>
	Host name of machine
	</arg>

	<param type='boolean' name='profile'>
	If 'yes', output a hash for the host(s) profile.
	Default is 'no'.
	</param>

	<example cmd='list host hash backend-0-0'>
	Create an install hash for backend-0-0.
	</example>
	"""

	def directoryhash(self, path):
		m = hashlib.md5()

		for dirpath, dirnames, filenames in os.walk(path):
			for f in filenames:
				filepath = os.path.join(dirpath, f)
				filestat = os.stat(filepath)
				fsize = '%d' % filestat.st_size
				fmtime = '%d' % filestat.st_mtime

				buf = '%s %s %s\n' % (os.path.join(dirpath, f), fsize, fmtime)

				m.update(buf.encode())

		return m.hexdigest()


	def run(self, params, args):

		(profile, ) = self.fillParams([
			('profile', 'n') ])

		self.beginOutput()

		hosts = self.getHostnames(args)
		for host in hosts:
			#
			# calculate MD5s for the pallets associated with the host
			#
			box = self.getHostAttr(host, 'box')
			for pallet in self.getBoxPallets(box):
				path = '/export/stack/pallets/%s/%s/%s/%s/%s' % \
					(pallet.name, pallet.version, pallet.rel, pallet.os, pallet.arch)

				dirhash = self.directoryhash(path)
				self.addOutput(host, '%s  %s' % (dirhash, pallet.name))

			#
			# calculate MD5s for the carts associated with the host
			#
			contents = self.call('list.box', [ box ])
			if len(contents) > 0:
				for name in contents[0]['carts'].split():
					path = '/export/stack/carts/%s' % name
					dirhash = self.directoryhash(path)
					self.addOutput(host, '%s  %s' % (dirhash, name))

			if self.str2bool(profile):
				import subprocess

				p = subprocess.Popen(
					'/opt/stack/bin/stack list host profile hash=y %s' % host,
					stdin=subprocess.PIPE,
					stdout=subprocess.PIPE,
					stderr=subprocess.PIPE, shell=True)

				(o, e) = p.communicate()
				line = e.decode()

				#
				# strip off the last carriage return
				#
				if line[-1] == '\n':
					hashline = line[:-1]
				else:
					hashline = line

				self.addOutput(host, '%s' % hashline)

		self.endOutput(padChar='', trimOwner=True)

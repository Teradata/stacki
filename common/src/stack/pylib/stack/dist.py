#! /opt/stack/bin/python
#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
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
import types
import stack.file


class Arch:
	"""
	Base class that understands Linux architecture strings and nothing
	else.  All distributions needs this information as do other code
	that handles rpms
	"""

	def __init__(self):
		self.arch	= ''
		self.distArch	= ''
		self.cpus	= []
		self.i86cpus	= [ 'athlon', 'i686', 'i586', 'i486', 'i386' ]

	def getCPUs(self):
		return self.cpus

	def getArch(self):
		return self.arch

	def getDistArch(self):
		return self.distArch

	def setArch(self, arch, distArch=None):
		"""
		The two architectures are to handle trends like
		the AMD64 dist arch, where the true arch is x86_64.
		NOTE: This trend does not exist with RHEL.
		"""

		self.arch = arch
		if arch in self.i86cpus:
			self.cpus = self.i86cpus
			self.arch = 'i386'
		elif arch == 'x86_64':
			self.cpus = [ arch ]
			self.cpus.extend([ 'amd64', 'ia32e' ])
			self.cpus.extend(self.i86cpus)
		elif arch in [ 'armv7hl' ]:
			self.cpus = [ arch, 'armhf' ]
		else:
			self.cpus = [ arch ]

		self.cpus.extend([ 'src', 'noarch' ])

		if distArch:
			self.distArch = distArch
		else:
			self.distArch = arch

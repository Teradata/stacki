#!/opt/stack/bin/python
#
# @SI_Copyright@
#                             www.stacki.com
#                                  v2.0
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
import os.path
import sys
import stack.app
import stack.bootable
import stack.file
from stack.dist import DistError


class Distribution:

	def __init__(self, arch, name='default'):
		self.arch = arch
		self.tree = None
		self.name = name

		#
		# the 'native' cpu is always first
		#
		native = os.uname()[4]
		self.cpus = [ native, 'noarch' ]

	def getPath(self):
		return os.path.join(self.name, self.arch)
		
	def generate(self, flags=""):
		if not os.path.exists('default'):
			stack.util.system('/opt/stack/bin/stack ' +
				'create distribution resolve=true inplace=true ' +
				'md5=false')

		self.tree = stack.file.Tree(os.path.join(os.getcwd(), 
			self.getPath()))
		
	def getRPMS(self):
		return self.tree.getFiles(os.path.join('RedHat', 'RPMS'))

	def getSRPMS(self):
		return self.tree.getFiles('SRPMS')
		
	def getRPM(self, name):
		l = []
		for rpm in self.getRPMS():
			try:
				if rpm.getPackageName() == name:
					l.append(rpm)
			except:
				pass
		if len(l) > 0:
			return l
		return None

	

class App(stack.app.Application):
	def __init__(self, argv):
		stack.app.Application.__init__(self, argv)
		self.usage_name = 'build-initrd'
		self.usage_version = '@VERSION@'
		self.rpmsPath = None

		self.getopt.l.extend([
			('rpms=', 'Path to Local RPMs'),
			('pkgs=', 'RPM packages to add to initrd.img'),
			('update-pkgs=',
			'RPM packages to add to /updates in initrd.img'),
			('build-directory=',
				'Directory to apply all RPMs to')
		])

	def parseArg(self, c):
		if stack.app.Application.parseArg(self, c):
			return 1
		elif c[0] == '--rpms':
			self.rpmsPath = c[1]
		elif c[0] == '--pkgs':
			self.pkgs = c[1].split()
		elif c[0] == '--update-pkgs':
			self.updatepkgs = c[1].split()
		elif c[0] == '--build-directory':
			self.builddir = c[1]
		return 0


	def thinkLocally(self, name):
		assert self.rpmsPath

		print('thinkLocally: rpmsPath (%s)' % self.rpmsPath)
		localtree = stack.file.Tree(self.rpmsPath)

		locallist = {}
		for dir in localtree.getDirs():
			for rpm in localtree.getFiles(dir):
				for arch in self.dist.cpus:
					s = '%s-%s' % (name, arch)
					if s == rpm.getUniqueName():
						print("thinkLocally: found", rpm.getName())
						return rpm

		return None


	def overlaypkgs(self, pkgs, update):
		for pkg in pkgs:
			RPM = self.thinkLocally(pkg)
			if not RPM:
				RPM = self.boot.getBestRPM(pkg)

			if not RPM:
				raise DistError, "Could not find %s rpm" % (pkg)

			print("Applying package %s" % (pkg))

			self.boot.applyRPM(RPM, 
				os.path.join(os.getcwd(), pkg),
					flags='--noscripts --excludedocs')

			#
			# now 'overlay' the package onto the expanded initrd
			#
			destdir = '../%s' % self.builddir
			if update == 1:
				destdir = '%s/updates' % destdir

			os.system('cd %s ; find . -not -type d | cpio -pdu %s'
				% (pkg, destdir))


	def run(self):

		print("build-initrd starting...")
		print("arch:", self.getArch())

		self.dist = Distribution(self.getArch())
		self.dist.generate()

		self.boot = stack.bootable.Bootable(self.dist, 'none')

		print('updatepkgs: ' , self.updatepkgs)
		print('pkgs: ' , self.pkgs)

		#
		# overlay packages onto the initrd.img
		#
		update = 1 
		self.overlaypkgs(self.updatepkgs, update)

		update = 0
		self.overlaypkgs(self.pkgs, update)

		print("build-initrd complete.")

# Main
app = App(sys.argv)
app.parseArgs()
app.run()


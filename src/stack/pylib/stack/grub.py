#! /opt/stack/bin/python
#
# Writes the /boot/grub/stack.conf file, based on grub.conf.
# Used during postAction of kickstart.
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

import string
import os

class App:

	def __init__(self):
		self.defaultargs = 'ramdisk_size=150000 kssendmac '
		self.setFilename('stack.conf')
		self.title = 'Stack Reinstall'
		self.installKernel = 'kickstart/default/vmlinuz'  
		self.installRamdisk = 'kickstart/default/initrd.img'

	def getFilename(self, name):
		return self.filename

	def setFilename(self, name):
		self.filename = '/boot/grub/%s' % name

	def getBootTitle(self, name):
		return self.title

	def setBootTitle(self, name):
		self.title = name

	def getInstallKernel(self, name):
		return self.installKernel

	def setInstallKernel(self, name):
		self.installKernel = name

	def getInstallRamdisk(self, name):
		return self.installRamdisk

	def setInstallRamdisk(self, name):
		self.installRamdisk = name

	def run(self, args=''):
		"""Write the /boot/grub/stack.conf file. Extra arguments
		are used for frontend Reinstall."""

		original = '/boot/grub/grub-orig.conf'
		if not os.path.exists(original):
			original = '/boot/grub/grub.conf'

		while True:
			try:
				if os.stat(original)[6] > 0:
					break
			except:
				pass
				
		file = open(original, 'r')
		outfile = open(self.filename, 'w')

		saveit = 0
		orig_kernels = []

		for line in file.readlines():
			tokens = string.split(line)

			if tokens[0] == 'kernel':
				kernelpath = os.path.dirname(tokens[1])
				kernelflags = string.join(tokens[2:])
			elif tokens[0] == 'root':
				root = line
			elif tokens[0] != 'title' and \
				tokens[0] != 'initrd' and tokens[0] != 'module':

				#
				# Write the header
				#
				outfile.write(line)

			if tokens[0] == 'title':
				saveit = 1

			if saveit:
				orig_kernels.append(line)

		file.close()

		#
		# write the stack reinstall grub configuration file
		#
		outfile.write('title %s\n' % self.title)
		outfile.write(root)
		outfile.write('\tkernel %s/%s %s ' \
			% (kernelpath, self.installKernel, kernelflags))
		outfile.write(self.defaultargs)
		if args:
			outfile.write(args)
		outfile.write('\n')
		outfile.write('\tinitrd %s/%s\n' \
			% (kernelpath, self.installRamdisk))

		for line in orig_kernels:
			outfile.write(line)

		outfile.close()
		
		
	def append(self, args):
		"""Append kernel args to an existing grub conf file."""
		
		#
		# append the user-supplied arguments
		#
		gotTitle = 0
		contents = ''

		infile = open(self.filename, 'r')
		for line in infile.readlines():
			if line.count(self.title):
				gotTitle = 1

			l = line.split()

			if gotTitle and len(l) > 1 and l[1].count('vmlinuz'):
				contents += "%s %s\n" % (line[:-1], args)
				gotTitle = 0
				continue

			contents += line
		infile.close()
		
		outfile = open(self.filename, 'w')
		outfile.write(contents)
		outfile.close()
			
			

if __name__ == "__main__":
	app=App()
	app.run()

#!@PYTHON@

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

# $Id$
# $Log$
# Revision 1.6  2010/09/07 23:53:08  bruno
# star power for gb
#
# Revision 1.5  2009/05/01 19:07:08  mjk
# chimi con queso
#
# Revision 1.4  2008/10/18 00:56:02  mjk
# copyright 5.1
#
# Revision 1.3  2008/03/06 23:41:44  mjk
# copyright storm on
#
# Revision 1.2  2007/10/10 23:07:59  anoop
# Thinning down Pylib a little more. Moving classes that are used
# by single commands into the command structure away from pylib.
# The roll-<rollname>.xml file now supports "os" parameter
#
# Revision 1.1  2007/09/25 21:56:03  anoop
# Made the jumpstart config generator a bit more http aware. Still an ugly kludge
# that the Sun engineers should work on, to get native http support into pfinstall
#

import os
import sys
import string
import stack

class js:
	def __init__(self):
		
		# JumpStart Directories
		self.js_dir	= "/export/home/install/jumpstart"
		self.js_media	= os.path.join(js_dir, 'media')
		self.js_config	= os.path.join(js_dir, 'config')
		self.js_roll	= os.path.join(js_dir, 'rolls')

		# List of files to cpio. Populated by subsequent functions
		self.cpio_list = []

	def check_cd(self):
		print "Checking CDROM......\n"
		sys.stdout.flush()
			
		# Make sure it's a Solaris CDROM.
		f = open('%s/.cdtoc' % self.cdrom_mount, 'r')
		r = f.readlines()
		solaris_cdrom_flag = 0
		for i in r:
			if i.find("Solaris") != -1:
				solaris_cdrom_flag = 1
				break
		if solaris_cdrom_flag == 0:
			raise IOError

		print "Valid Solaris CDROM Found"	
		sys.stdout.flush()
	
	def spinner(self, p):
		# Fancy spinning wheel to denote progress
		find_done = 0
		x = 0
		spinner = ['/\b','-\b','\\\b','|\b']
		while not find_done:
			if p.poll() == -1:
				sys.stdout.write(spinner[x%4])
				sys.stdout.flush()
				x=x+1
				time.sleep(0.5)
			else:
				find_done = 1
		print "Done"	
		sys.stdout.flush()
		
	def cpio(self):
		p = popen2.Popen3('time -p cpio -mpud %s' % self.js_media)
		p.tochild.write("%s" % '\n'.join(self.cpio_list))
		p.tochild.close()
		self.spinner(p)

	def scanner(self, dir):
		# Must be overridden by derived classes
		pass
		
class js_sunos(js):
	def __init__(self):
		js.__init__(self)
		
		# CDROM Directory
		if os.path.exists("/cdrom/cdrom0"):
			self.cdrom_mount = "/cdrom/cdrom0"
		else:
			self.cdrom_mount = "/cdrom"
		# Package listing. Can only be used on a Solaris machine.
		self.pkg_list = []
	
	def scanner(self, dirname):
		""" Scans a particular directory to get a list
		of all files that need to be copied, and a list
		of all packages that need to be translated and
		copied"""

		# Get current working directory
		cur_dir = os.getcwd()
		# Change to specified directory
		os.chdir(dirname)
		for i in os.listdir(dirname):
			if os.path.isfile(os.path.join(dirname,i)):
				self.cpio_list.append(os.path.join(dirname,i))
			if os.path.isdir(os.path.join(dirname,i)) and \
				not os.path.exists(os.path.join(dirname,i,"pkgmap")):
				self.scanner(os.path.join(dirname,i))
			if os.path.isdir(os.path.join(dirname,i)) and \
				os.path.exists(os.path.join(dirname,i,"pkgmap")):
				self.pkg_list.append(os.path.join(dirname,i))
		os.chdir(cur_dir)
		
	def trans_package(self):
		# Transfer the packages from the filesystem format on DVD
		# to the datastream format on to disk
		for i in pkg_list:
			pkg_src = os.dirname(i)
			pkg_name = os.basename(i)
			os.system('pkgtrans -s %s %s %s' % (i, pkg_src, pkg_name))

class js_linux(js):
	def __init__(self):
		js.__init__(self)

		# CDROM Directory
		cdrom_mount = "/mnt/cdrom"
		
	def scanner(self, dirname):
		""" Scans a particular directory to get a list
		of all files that need to be copied. In the case
		of Linux, that's just all the files/directories
		that are present on the CD. No exceptions.
		"""
		# Get current working directory
		cur_dir = os.getcwd()
		# Change to specified directory
		os.chdir(dirname)
		for i in os.listdir(dirname):
			self.cpio_list.append(os.path.join(dirname,i))
			self.scanner(os.path.join(dirname,i))
		os.chdir(cur_dir)

class clustertoc_parse:
	def __init__(self, root_cluster):
		
		self.js_dir = '/export/home/install/jumpstart'
		self.js_media = os.path.join(self.js_dir,'media')
		self.js_clustertoc = os.path.join(self.js_media,
				'Solaris_10/Product/.clustertoc')
		
		self.clustertoc = open(self.js_clustertoc)
		self.root = root_cluster
		self.pkg_hier = {}
		self.pkg_list = []
		self.parse()
		self.traverse(self.root)
	
	def parse(self):
		r = self.clustertoc.readlines()
		read_state = 'none'
		for i in r:
			if i.startswith('END'):
				read_state = 'none'
				continue
			member_name = i.strip().split('=')[1]
			if i.startswith('CLUSTER=') or i.startswith('METACLUSTER='):
				cluster_name = member_name
				read_state = 'cluster'
				self.pkg_hier[cluster_name] = []
			if i.startswith('SUNW_CSRMEMBER'):
				if read_state == 'cluster':
					self.pkg_hier[cluster_name].append(member_name)

	def traverse(self, start_point):
		try:
			for i in self.pkg_hier[start_point]:
				self.traverse(i)
		except KeyError:
			self.pkg_list.append(start_point)
		
	def printer(self, start_point='SUNWCXall'):
		#for i in self.pkg_hier:
		#	print i
		#	print self.pkg_hier[i]

		self.traverse(start_point)
		print "LIST OF ITEMS IN CLUSTER : %s" % (start_point)
		print '\n'.join(self.pkg_list)

#! /opt/stack/bin/python
# 
# @Copyright@
#				Rocks(r)
#			 www.rocksclusters.org
#			 version 5.4 (Maverick)
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
#	"This product includes software developed by the Rocks(r)
#	Cluster Group at the San Diego Supercomputer Center at the
#	University of California, San Diego and its contributors."
# 
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.  The name of the
# software includes the following terms, and any derivatives thereof:
# "Rocks", "Rocks Clusters", and "Avalanche Installer".	 For licensing of 
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


import os
import xml.dom.minidom
import stack.file
import stack.util


class KickstartFile:

	def __init__(self, distribution):
		self.dist = distribution
		self.root = ''
		self.kgenFlags = ''
		self.kppFlags = ''
		
	def setRoot(self, root):
		self.root = ''
		
	def setKgenFlags(self, flags):
		self.kgenFlags = flags

	def setKppFlags(self, flags):
		self.kppFlags = flags
		
	def generate(self, start):
		"""Generate a kickstart file starting at the given graph node"""	
		# Kickstart_LocalRolldir is appended to the URL for the
		# bootstrap kickstart file that is found on the CD

		if self.root:
			os.environ['Kickstart_LocalRolldir'] = os.path.join('/',
				self.root)
		os.environ['Node_Hostname'] = 'BOOTSTRAP' # silences errors

		cwd = os.getcwd()
		os.chdir(os.path.join(self.dist.name, self.dist.arch, 'build'))
		list = []
		cmd = 'kpp %s %s | kgen %s' % (self.kppFlags, start,
			self.kgenFlags)
		for line in os.popen(cmd).readlines():
			list.append(line[:-1])
		os.chdir(cwd)
		return list
		


class Distribution:

	def __init__(self, arch, name='default'):
		self.arch = arch
		self.tree = None
		self.name = name
	
	def getPath(self):
		return os.path.join(self.name, self.arch)
		
	def generate(self, md5=True, resolve=True):
		flags = 'inplace=true'
		if not md5:
			flags += ' md5=false'
		if resolve:
			flags += ' resolve=true'
		stack.util.system('/opt/stack/bin/stack create distribution %s %s' % 
				  (self.name, flags))
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


	
class Generator():
	def __init__(self):
		self.rolls = []
		self.os = os.uname()[0].lower()

	##
	## Parsing Section
	##
	def parse(self, file):
		doc  = xml.dom.minidom.parseFile(file)
		node = doc.getElementsByTagName('roll')

		attr = node.attributes
		if attr.getNamedItem((None, 'name')):
			name = attr.getNamedItem((None, 'name')).value
		else:
			name = ''

		if attr.getNamedItem((None, 'version')):
			version = attr.getNamedItem((None, 'version')).value
		else:
			version = ''

		if attr.getNamedItem((None, 'arch')):
			arch = attr.getNamedItem((None, 'arch')).value
		else:
			arch = ''

		if attr.getNamedItem((None, 'url')):
			url = attr.getNamedItem((None, 'url')).value
		else:
			url = ''

		if attr.getNamedItem((None, 'diskid')):
			diskid = attr.getNamedItem((None, 'diskid')).value
		else:
			diskid = ''

		if attr.getNamedItem((None, 'release')):
			release = attr.getNamedItem((None, 'release')).value
		else:
			release = ''

		self.rolls.append((name, version, release, arch, url, diskid))



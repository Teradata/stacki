#! /opt/stack/bin/python
# 
# @SI_Copyright@
#                               stacki.com
#                                  v3.3
# 
#      Copyright (c) 2006 - 2016 StackIQ Inc. All rights reserved.
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


import os
import types
import string
import stack.file
import stack.ks
import xml.sax

class DistError(Exception):
	pass
	
class DistRPMList(DistError):
	def __init__(self, list):
		Exception.__init__(self, list)
		self.list = list

	
# All the 'get()' functions return None on failure.

class Arch:
	"""Base class that understands Linux architecture strings and nothing
	else.  All distributions needs this information as do other code
	that handles rpms"""
	
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
		"""The two architectures are to handle trends like
		the AMD64 dist arch, where the true arch is x86_64.
		NOTE: This trend does not exist with RHEL."""
		
		self.arch = arch
		if arch in self.i86cpus:
			self.cpus = self.i86cpus
			self.arch = 'i386'
		elif arch == 'x86_64':
			self.cpus = [ arch ]
			self.cpus.extend([ 'ia32e' ])
			self.cpus.extend(self.i86cpus)
		else:
			self.cpus = [ arch ]

		self.cpus.extend([ 'src', 'noarch' ])
		
		if distArch:
			self.distArch = distArch
		else:
			self.distArch = arch



		
class Base(Arch):
	"""Understands how to navigate the sometimes arcane 
	RedHat linux distribution directory paths. Used to build
	and manipulate custom RedHat-compatible distributions."""

	def __init__(self):
		Arch.__init__(self)
		self.root       = ''
		self.distdir	= ''
		self.trees	= {}

	def isBuilt(self):
		if self.trees != {}:
			return 1
		else:
			return 0

	def build(self):
		self.trees['release'] = stack.file.Tree(self.getReleasePath())

	def setRoot(self, s):
		self.root = s
		
	def setDist(self, d):
		self.distdir = d
		
	def getDist(self):
		return self.distdir

	def getRootPath(self):
		return self.root

	def getHomePath(self):
		return os.path.join(self.root, self.distdir)

	def getReleasePath(self):
		return os.path.join(self.getHomePath(), self.getDistArch())

	def getWANReleasePath(self, client='all'):
		return os.path.join(self.getHomePath(), client, 
			self.getDistArch())

	def getRPMSPath(self):
		return os.path.join(self.getReleasePath(), 'RedHat', 'RPMS')

    
	def getBasePath(self):
		return os.path.join(self.getReleasePath(), 'RedHat', 'base')
		

	def getRollCentralPath(self):
		return str(os.path.join(self.getHomePath(), 'pallets'))

        
	def getBaseFile(self, name):
		for file in self.getFiles('release',
					  os.path.join('RedHat', 'base')):
			if file.getName() == name:
				return file
		return None

	def getTreeNames(self):
		return self.trees.keys()

	def getTree(self, name):
		if name in self.trees.keys():
			return self.trees[name]
		else:
			return None

	def setFiles(self, name, path, list):
		self.trees[name].setFiles(path, list)

	def getFiles(self, name, path):
		try:
			value = self.trees[name]
		except KeyError:
			return []
		list = [] 
		if type(value) == types.ListType:
			for tree in value:
				list.extend(tree.getFiles(path))
			return list
		else:
			return value.getFiles(path)

	def setBaseFiles(self, list):
		self.setFiles('release', os.path.join('RedHat', 'base'), list)

	def setRPMS(self, list):
		self.setFiles('release', os.path.join('RedHat', 'RPMS'), list)

	def setLiveOS(self, list):
		self.setFiles('release', os.path.join('LiveOS'), list)
        
	def getPackage(self, name, list):

		pkg = {}
		for file in list:
			if file.getBaseName() == name:
				arch = file.getPackageArch()
				if pkg.has_key(arch):
					# Already have a package for the arch, need to
					# decide which one to use.
					orig = pkg[arch]
					if file > orig:
						pkg[arch] = file
				else:
					pkg[arch] = file

		matches = []
		for key in pkg.keys():
			matches.append(pkg[key])

		
		if not matches:
			return None
		elif len(matches) == 1:
			return matches[0]
		else:
			raise DistRPMList(matches)

	def getRPM(self, name):
		return self.getPackage(name, self.getRPMS())
		
	def getRPMS(self):
		return self.getFiles('release', os.path.join('RedHat', 'RPMS'))

	def getReleaseTree(self):
		return self.getTree('release')

	def dumpDirNames(self):
		for key in self.trees.keys():
			value = self.trees[key]
			if type(value) == types.ListType:
				for e in value:
					e.dumpDirNames()
			else:
				value.dumpDirNames()
        
	def dump(self):
		for key in self.trees.keys():
			value = self.trees[key]
			if type(value) == types.ListType:
				for e in value:
					e.dump()
			else:
				value.dump()


        
class Mirror(Base):

	def __init__(self, mirror=None):
		Base.__init__(self)
		if mirror:
			self.setHost(mirror.host)
			self.setPath(mirror.dir)
			self.setRoot(mirror.root)
			self.setArch(mirror.arch, mirror.distArch)
		else:
			self.host	= ''
			self.dir	= ''
		self.getRelease = 1



	def __str__(self):
		s = "Stack Mirror Distribution\n"
		s += "Host: %s\n" % self.getHost()
		s += "Path: %s\n" % self.getPath()
		return s

	def __cmp__(self, other):
		if not other:
			return -1
		elif other.getHost() == self.getHost() and \
			other.getPath() == self.getPath():
			return 0
		else:
			return -1

	def build(self):
		Base.build(self)
		self.trees['pallets'] = stack.file.Tree(self.getRollsPath())

	def getRootPath(self):
		return self.root

	def setHost(self, s):
		self.host = s

	def setPath(self, s):
		self.dir = s

	def getHost(self):
		return self.host

	def getPath(self):
		return self.dir
    
	def getHomePath(self):
		return os.path.join(self.root, self.host, self.dir)

	def getRemoteReleasePath(self):
		return os.path.join(self.dir, self.getDistArch())

	def getRollsPath(self):
		return os.path.join(self.getRootPath(), 'pallets')


	def getRollRPMS(self, roll, version, arch):

		# Support both old (/version/arch/RedHat) and new
		# (/version/os/arch) layout for pallets.
		
		path  = os.path.join(roll, version, 'redhat', arch, 'RPMS')
		files = self.getFiles('pallets', path)
		if not files:
			path  = os.path.join(roll, version, arch,
					     'RedHat', 'RPMS')
			files = self.getFiles('pallets', path)
		return files


	def getRollBaseFiles(self, roll, version, arch):
		"""
		This is used to get the comps.xml from the kernel Roll.
		"""

		# Support both old (/version/arch/RedHat) and new
		# (/version/redhat/arch) layout for pallets.
		
		path  = os.path.join(roll, version, 'redhat', arch, 'RedHat',
			'base')
		files = self.getFiles('pallets', path)
		if not files:
			path  = os.path.join(roll, version, arch, 'RedHat', 'base')
			files = self.getFiles('pallets', path)
		return files
		

	def getRollLiveOSFiles(self, roll, version, arch):
		"""
		Used to get all files in 'LiveOS' directory
		"""

		#
		# only support the new roll layout -- since this was added
		# for RHEL 7
		#
		path = os.path.join(roll, version, 'redhat', arch, 'LiveOS')
		return self.getFiles('pallets', path)
		

	def getRolls(self):
		rolls = {}
		rollsPath = self.getRollsPath()
		if not os.path.exists(rollsPath):
			return rolls
		for r in os.listdir(rollsPath):
			rolls[r] = []
			rdir = os.path.join(self.getRollsPath(), r)
			if not os.path.isdir(rdir):
				continue
			for v in os.listdir(rdir): # version
				vdir = os.path.join(rdir, v)
				if not os.path.isdir(vdir):
					continue
				for o in os.listdir(vdir): # os
					odir = os.path.join(vdir, o)
					if not os.path.isdir(odir):
						continue

					a = None
					for a in os.listdir(odir): # arch
						adir = os.path.join(odir, a)
						if not os.path.isdir(adir):
							continue

					# If this is not a RedHat Roll ignore
					# it.
					#
					# New style is version/os/arch, which
					# breaks the old style of version/arch.
					# So, for now (kill this code after a
					# few releases) if the detected os is
					# "x86_64" assume this is a redhat Roll.
					# Why?  3rd party Rolls for Rocks+ 6.0
					# should still work with 6.0.2 (eg Intel
					# QLogic Roll).  Also means we don't
					# need to rebuild everything, and good
					# for bootstrapping to the new directory
					# hierarchy.
					#
					# Similar code is needed when we go
					# back and read the files.

					if not a:
						continue
						
					if o != 'redhat':
						if o in ['x86_64', 'i386']:
							a = o
							o = 'redhat'
						else: # not for redhat skip it
							continue
						
					rolls[r].append((v, a))

		return rolls


class Distribution(Base):

	def __init__(self, m, v):
		Base.__init__(self)
		self.contrib		= ''
		self.siteprofiles	= ''
		self.local		= ''
		self.mirrors		= m
		self.root		= self.mirrors[0].root
		self.arch		= self.mirrors[0].arch
		self.distArch 		= self.mirrors[0].distArch
		self.cpus		= self.mirrors[0].cpus
		self.version		= v

	def build(self):
		Base.build(self)
		self.trees['contrib'] = stack.file.Tree(self.contrib)
		self.trees['force'] = stack.file.Tree(self.getForceRPMSPath())
		self.trees['site-profiles'] = stack.file.Tree(self.siteprofiles)
		self.trees['local'] = []
		self.trees['local_srpms'] = []
		self.trees['cdrom'] = []
		self.trees['pallets'] = []
		for e in self.getSiteRPMSPath():
			self.trees['local'].append(stack.file.Tree(e))
		# make the force tree imortal
		for f in self.trees['force'].getFiles(''):
			f.setImortal()


	def setContrib(self, s):
		self.contrib = s

	def setSiteProfiles(self, s):
		self.siteprofiles = s

	def setLocal(self, s):
		self.local = s
		
	def getStackRelease(self):
		return self.version
    
	def getBuildPath(self):
		return os.path.join(self.getReleasePath(), 'build')
    
	def getKickstartFile(self, file, distdir=None):
		cwd = os.getcwd()
		os.chdir(self.getRootPath())
		retval = stack.ks.KickstartFile(file, self.arch, distdir)
		os.chdir(cwd)
		return retval

	def getSiteRPMSPath(self):
		l = []
		if self.local:
			for cpu in self.cpus:
				l.append(os.path.join(self.local, 'RPMS', cpu))
		if os.environ.has_key('RPMHOME'):
			for cpu in self.cpus:
				l.append(os.path.join(os.environ['RPMHOME'],
						      'RPMS', cpu))
		return l

	def getForceRPMSPath(self):
		return os.path.join(self.getReleasePath(), 'force', 'RPMS')

	def getRollsPath(self):
		return os.path.join(self.getReleasePath(), 'pallets')

	def getContribRPMSPath(self):
		return os.path.join(self.contrib, self.arch, 'RPMS')

	def getMirrors(self):
		return self.mirrors

	def getContribRPMS(self):
		return self.getFiles('contrib', os.path.join(self.arch, 'RPMS'))

	def getLocalRPMS(self):
		return self.getFiles('local', '')

	def getForceRPMS(self):
		return self.getFiles('force', '')

	def getSiteProfilesTree(self):
		return self.getTree('site-profiles')

	def syncMirror(self):
		for mirror in self.mirrors:
			tree = mirror.getTree('release')
			for key in tree.getDirs():
				self.getTree('release').\
				setFiles(key, tree.getFiles(key))



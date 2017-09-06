#! /opt/stack/bin/python
# 
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
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



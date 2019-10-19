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
import string
import re
import shutil
import stack.util
import stack.probepal
import xml.sax
import subprocess
try:
	import rpm
except ImportError:
	pass


class File:
    
	def __init__(self, file, timestamp=None, size=None):
		# Timestamp and size can be explicitly set for foreign files.
		self.setFile(file, timestamp, size)
		self.imortal = 0

	def __eq__(self, file):
		return self.__cmp__(file) == 0

	def __ne__(self, file):
		return self.__cmp__(file) != 0

	def __lt__(self, file):
		return self.__cmp__(file) < 0

	def __le__(self, file):
		return self.__cmp__(file) <= 0

	def __gt__(self, file):
		return self.__cmp__(file) > 0

	def __ge__(self, file):
		return self.__cmp__(file) >= 0

	def __cmp__(self, file):
		if self.getBaseName() != file.getBaseName() or self.timestamp == file.timestamp:
			rc = 0
		elif self.timestamp > file.timestamp:
			rc = 1
		else:
			rc = -1

		# Override the inequality determination and base the decision
		# on the imortal flag.	If both files are divine, than don't
		# change anything.
	
		if rc and self.imortal + file.imortal == 1:
			if self.imortal:
				rc = 1
			else:
				rc = -1
		
		return rc

	def setFile(self, file, timestamp=None, size=None):
		self.pathname	= os.path.dirname(file)
		self.filename	= os.path.basename(file)

		if not os.path.exists(file):
			self.timestamp = 0
			self.size = 0
		else:
			# Get the timestamp of the file, or the derefereneced
			# symbolic link. If the dereferenced link does not
			# exist set the timestamp to zero.

			if None not in (timestamp, size):
				self.timestamp = timestamp
				self.size = size
			elif not os.path.islink(file):
				self.timestamp = os.path.getmtime(file)
				self.size = os.path.getsize(file)
			else:
				orig = os.readlink(file)
				if os.path.isfile(orig):
					self.timestamp = os.path.getmtime(orig)
					self.size = os.path.getsize(file)
				else:
					self.timestamp = 0
					self.size = 0

	def explode(self):

		# If the file is a symbolic link to a file, follow the link
		# and copy the file.	 Links to directories are not exanded.

		file = self.getFullName()
		if os.path.islink(file):
			orig = os.readlink(file)
			if os.path.isfile(orig):
				os.unlink(file)
				shutil.copy2(orig, file)
		
				# Fix the timestamp back to that of 
				# the original file. The above copy seems 
				# to do this for us, but I'm going to 
				# leave this in to make sure it always works.
		
				tm = os.path.getmtime(orig)
				os.utime(file, (tm, tm))
		
	def setImortal(self):
		self.imortal = 1
	
	def getTimestamp(self):
		return self.timestamp

	def getSize(self):
		return float(self.size) / (1024 * 1024)
    
	def getUniqueName(self):
		return self.filename

	def getBaseName(self):
		return self.filename
    
	def getName(self):
		return self.filename

	def getShortName(self):
		return os.path.splitext(self.filename)[0]

	def getPath(self):
		return self.pathname

	def getFullName(self):
		return str(os.path.join(self.pathname, self.filename))

	def symlink(self, target, base=''):
		if os.path.isfile(target) or os.path.islink(target):
			os.unlink(target)
		os.symlink(self.getFullName(), target)

	def chmod(self, mode):
		if os.path.exists(self.getFullName()):
			os.chmod(self.getFullName(), mode)

	def dump(self):
		print('%s(%s)' % (self.filename, self.pathname))



class RPMBaseFile(File):

	def __init__(self, file, timestamp=None, size=None, ext=1):
		File.__init__(self, file, timestamp, size)

		self.list = []
		self.version = None
		self.release = None

		rpmcmd = ['rpm', '-qp', file, '--queryformat', "%{NAME} %{VERSION} %{RELEASE} %{ARCH}"]
		p = subprocess.Popen(rpmcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		rc = p.wait()
		o, e = p.communicate()
		if rc == 0:
			self.list = o.decode().split()
		else:
			print("Skipping %s - %s" % (file, e.decode()))

	def getBaseName(self):
		return self.list[0]

	def getUniqueName(self):
		return '%s-%s' % (self.list[0], self.list[3])



class RPMFile(RPMBaseFile):

	def __init__(self, file, timestamp=None, size=None):
		RPMBaseFile.__init__(self, file, timestamp, size)
	
	def __cmp__(self, file):
		if self.getPackageArch() != file.getPackageArch():
			rc = 0
		else:
			rc = File.__cmp__(self, file)
		return rc

	def getPackageName(self):
		return self.getBaseName()

	def getPackageVersion(self):
		return self.list[1]

	def getPackageRelease(self):
		return self.list[2]

	def getPackageVersionString(self):
		return self.version

	def getPackageReleaseString(self):
		return self.release

	def getPackageArch(self):
		return self.list[3]
		
	def installPackage(self, root, flags=""):
		"""Installs the RPM at the given root directory.  This is
		used for patching RPMs into the distribution and making
		bootable CDs"""
		pass
		
		dbdir = os.path.join(root, 'var', 'lib', 'rpm')
		if not os.path.isdir(dbdir):
			os.makedirs(dbdir)
	
		cmd = 'rpm -i --nomd5 --force --nodeps --ignorearch ' + \
			'--dbpath %s %s ' % (dbdir, flags)
		cmd += '--badreloc --relocate /=%s %s' \
			% (root, self.getFullName())

		retval = os.system(cmd)
		
		# Crawl up from the end of the dbdir path and prune off
		# all the empty directories.		
		while dbdir:
			if not os.listdir(dbdir):
				shutil.rmtree(dbdir)
			list = dbdir.split(os.sep)
			dbdir = os.sep.join(list[:-1])

		return retval

		
class RollFile(File):
	def __init__(self, file, timestamp=None, size=None):
		try:
			File.__init__(self, file, timestamp, size)
		except:
			return

		cmd = 'mount -o loop %s /mnt/cdrom > /dev/null 2>&1' % \
			self.getFullName()
		retcode = os.system(cmd)
		if retcode:
			return

		pal = stack.probepal.Prober()
		pallets = pal.find_pallets('/mnt/cdrom')
		os.system('umount /mnt/cdrom > /dev/null 2>&1')

		# TODO always expect single pallet?
		pallet = pallets['/mnt/cdrom']
		if not pallet:
			return

		p = pallet[0]
		self.name = p.name
		self.version = p.version
		self.release = p.release
		self.arch = p.arch
		self.os = p.distro_family
		self.diskid = ''
		# TODO need foreign??
		# TODO mounting is fucked up


	def __cmp__(self, file):
		if self.getRollArch() != file.getRollArch():
			rc = 0
		else:
			rc = File.__cmp__(self, file)
		return rc

	def getRollName(self):
		return self.name

	def getRollVersion(self):
		return self.version

	def getRollRelease(self):
		return self.release

	def getRollArch(self):
		return self.arch


class RollInfoFile(File,
	xml.sax.handler.ContentHandler, xml.sax.handler.DTDHandler,
	xml.sax.handler.EntityResolver, xml.sax.handler.ErrorHandler):

	def __init__(self, file):
		File.__init__(self, file)
		
		self.attrs = {}
		parser = xml.sax.make_parser()
		parser.setContentHandler(self)
		fin = open(file, 'r')
		parser.parse(fin)
		fin.close()
		
	def startElement(self, name, attrs):
		self.attrs[str(name)] = {}
		for (attrName, attrVal) in attrs.items():
			self.attrs[str(name)][str(attrName)] = str(attrVal)
	
	def getXML(self):
		"""Regenerate the XML file based on what was read in and
		the current state."""
		
		xml = []
		
		xml.append('<roll name="%s" interface="%s">' %
			(self.getRollName(), self.getRollInterface()))
		for tag in self.attrs.keys():
			if tag == 'roll':
				continue
			attrs = ''
			for key, val in self.attrs[tag].items():
				attrs += ' %s="%s"' % (key, val)
			xml.append('\t<%s%s/>' % (tag, attrs))
		xml.append('</roll>')
		
		return '\n'.join(xml)
		
	def getRollName(self):
		return self.attrs['roll']['name']
		
	def getRollInterface(self):
		return self.attrs['roll']['interface']
		
	def getRollVersion(self):
		return self.attrs['info']['version']
	
	def getRollRelease(self):
		return self.attrs['info']['release']
		
	def setRollOS(self, os):
		if os == 'linux':	# linux really means redhat
			os = 'redhat'
		self.attrs['info']['os'] = os
		
	def getRollOS(self):
		try:
			os = self.attrs['info']['os']
		except KeyError:
			os = 'linux'
		if os == 'linux':	# linux really means redhat
			os = 'redhat'
		return os

	def setRollArch(self, arch):
		self.attrs['info']['arch'] = arch

	def getRollArch(self):
		return self.attrs['info']['arch']
		
	def getISOMaxSize(self):
		return float(self.attrs['iso']['maxsize'])

	def setISOMaxSize(self, size):
		self.attrs['iso']['maxsize'] = size
		
	def getISOFlags(self):
		return self.attrs['iso']['mkisofs']
		
	def getRollRolls(self):
		return self.attrs['rpm']['rolls']

	def setBootable(self, bootable=True):
		x = 0
		if bootable:
			x = 1
		self.attrs['iso']['bootable'] = x

	def isBootable(self):
		return int(self.attrs['iso']['bootable'])

	def needsComps(self):
		return int(self.attrs['iso']['addcomps'])
		
	def hasRolls(self):
		if self.attrs['rpm']['rolls'] != '0':
			return 1
		else:
			return 0
		
	def hasRPMS(self):
		return int(self.attrs['rpm']['bin'])
		
	def hasSRPMS(self):
		return int(self.attrs['rpm']['src'])
		

class Tree:

	def __init__(self, root):
		self.root = root
		self.tree = {}
		self.build('')

	def getRoot(self):
		return self.root

	def getDirs(self):
		return self.tree.keys()

	def clear(self, path=''):
		l1 = path.split(os.sep)
		for key in self.tree.keys():
			l2 = key.split(os.sep)
			if stack.util.list_isprefix(l1, l2):
				del self.tree[key]
	
	def getFiles(self, path=''):
		try:
		    list = self.tree[path]
		except KeyError:
		    list = []
		return list

	def setFiles(self, path, files):
		self.tree[path] = files
	
	def build(self, dir):
		path = os.path.join(self.root, dir)
		if not os.path.isdir(path):
		    return

		# Handle the case where we don't have permission to traverse
		# into a tree by pruning off the protected sub-tree.
		try:
		    files = os.listdir(path)
		except:
		    files = []

		v = []
		for f in files:
			filepath = os.path.join(path, f)
			if os.path.isdir(filepath) and not os.path.islink(filepath):
				self.build(os.path.join(dir, f))
			else:
				if re.match('.*\.rpm$', f) is not None:
					v.append(RPMFile(filepath))
				elif re.match('roll-.*\.iso$', f) is not None:
					v.append(RollFile(filepath))
				else:
					v.append(File(filepath))
		self.tree[dir] = v

	def dumpDirNames(self):
		for key in self.tree.keys():
		    print(key)
	    
	def dump(self):
		self.apply(self.__dumpIter__)

	def apply(self, func, root=None):
		for key in self.tree.keys():
			for e in self.tree[key]:
				func(key, e, root)

	def __dumpIter__(self, path, file, root):
		print(path, end=' ')
		file.dump()

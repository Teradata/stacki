#! /opt/stack/bin/python
# 
# @SI_Copyright@
#                               stacki.com
#                                  v3.3
# 
#      Copyright (c) 2006 - 2017 StackIQ Inc. All rights reserved.
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
import sys
import os
import string
import re
import shutil
import stack.util
import xml.sax
try:
	import rpm
except ImportError:
	pass


class File:
    
	def __init__(self, file, timestamp=None, size=None):
		# Timestamp and size can be explicitly set for foreign files.
		self.setFile(file, timestamp, size)
		self.imortal = 0
	
	def __cmp__(self, file):
		if self.getBaseName() != file.getBaseName() or \
		 self.timestamp == file.timestamp:
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
		return float(self.size) / (1024*1024)
    
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

                fd = os.open(file, os.O_RDONLY)
		try:

                	ts = rpm.ts()
			ts.setVSFlags(rpm._RPMVSF_NOSIGNATURES)

			rpminfo = ts.hdrFromFdno(fd)

			basename = rpminfo[rpm.RPMTAG_NAME]
			arch = rpminfo[rpm.RPMTAG_ARCH]
			self.version = rpminfo[rpm.RPMTAG_VERSION]
			self.release = rpminfo[rpm.RPMTAG_RELEASE]

			self.list = [ basename, self.version, self.release,
				arch ]
		except:
			pass
		os.close(fd)

                if not len(self.list):
                        # Remove ext count extensions, the default is 1, but for
                        # rolls we remove two (.diskN.iso)
                
                        s = self.filename        # name-ver-rpmver.arch.rpm
                        for x in range(0, ext):
                                i = string.rfind(s, ".")
                                s = self.filename[:i]
    
                        i = string.rfind(s, ".")
                        self.list.append(s[i+1:])       # get architecture string
                        s = self.filename[:i]

                        i = string.rfind(s, "-")        # get RPM version string
                        self.release = s[i+1:]
                        self.list.append(self.versionList(s[i+1:]))
                        s = self.filename[:i]

                        i = string.rfind(s, "-")        # get software version string
                        self.version = s[i+1:]
                        self.list.append(self.versionList(s[i+1:]))

        
                        self.list.append(self.filename[:i]) # get package name
        
                        self.list.reverse()             # we built the list backwards


	def versionList(self, s):
		list = []
		for e in re.split('\.+|_+', s):
			num	= ''
			alpha	= ''
			l	= []
			for c in e:
				if c in string.digits:
					num = num + c
					if alpha:
						l.append(alpha)
						alpha = ''
				else:
					alpha = alpha + c
					if num:
						l.append(string.atoi(num))
						num = ''
			if alpha:
				l.append(alpha)
			if num:
				l.append(string.atol(num))
			list.append(l)
		return list

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
			list = string.split(dbdir, os.sep)
			dbdir = string.join(list[:-1], os.sep)

		return retval

		
class RollFile(File):
	def __init__(self, file, timestamp=None, size=None):
		try:
			File.__init__(self, file, timestamp, size)
		except:
			pass

		self.name, self.version, self.release, self.arch, \
			self.diskid, self.foreign = self.getRollInfo()

	def getRollInfoFromXML(self):
		name = None
		version = None
		release = None
		arch = None

		cdtree = stack.file.Tree('/mnt/cdrom')
		for dir in cdtree.getDirs():
			for file in cdtree.getFiles(dir):
				try:
					xmlfile = stack.file.RollInfoFile(
						file.getFullName())

					name = xmlfile.getRollName()
					version = xmlfile.getRollVersion()
					release = xmlfile.getRollRelease()
					arch = xmlfile.getRollArch()

					return name, version, release, arch
				except:
					continue

		return None, None, None, None

	def getRollInfo(self):
		name = None
		arch = None
		version = None
		release = None
		diskid = None
		foreign = 0

		cmd = 'mount -o loop %s /mnt/cdrom > /dev/null 2>&1' % \
			self.getFullName()
		retcode = os.system(cmd)
		if retcode:
			return name, version, release, arch, diskid, foreign

		if os.path.exists('/mnt/cdrom/.treeinfo'):
			foreign = 1
			file = open('/mnt/cdrom/.treeinfo', 'r')
			for line in file.readlines():
				a = line.split('=')

				if len(a) != 2:
					continue

				key = a[0].strip()
				value = a[1].strip()

				if key == 'family':
					if value == 'Red Hat Enterprise Linux':
						name = 'RHEL'
					elif value.startswith('CentOS'):
						name = 'CentOS'
					elif value == 'Oracle Linux Server':
						name = 'Oracle'
				elif key == 'version':
					version = value
				elif key == 'arch':
					arch = value
				elif key == 'discnum':
					diskid = value
			file.close()
		elif os.path.exists('/mnt/cdrom/.discinfo'):
			name, version, release, arch = self.getRollInfoFromXML()

			file = open('/mnt/cdrom/.discinfo', 'r')
			t = file.readline().strip()
			n = file.readline().strip()
			a = file.readline().strip()
			d = file.readline().strip()
			file.close()

			if not name:
				name = n.replace(' ', '_')
			if not arch:
				arch = a

			#
			# get the disk id if there are multiple disks, this
			# will be 1, 2, etc.
			#
			diskid = d

		if not name:
			name = "BaseOS"
			foreign = 1
		if not version:
			version = stack.version
		if not release:
			release = stack.release
		if not arch:
			arch = 'x86_64'
		if not diskid:
			diskid = '1'

		os.system('umount /mnt/cdrom')

		return name, version, release, arch, diskid, foreign

	def __cmp__(self, file):
		if self.getRollArch() != file.getRollArch():
			rc = 0
		else:
			rc = File.__cmp__(self, file)
		return rc

	def getRollDiskID(self):
		return self.diskid
		
	def getRollName(self):
		return self.name

	def getRollVersion(self):
		return self.version

	def getRollRelease(self):
		return self.release

	def getRollVersionString(self):
		return self.version

	def getRollReleaseString(self):
		return self.release

	def getRollArch(self):
		return self.arch

	def isRollForeign(self):
		return self.foreign


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
			for key,val in self.attrs[tag].items():
				attrs += ' %s="%s"' % (key, val)
			xml.append('\t<%s%s/>' % (tag, attrs))
		xml.append('</roll>')
		
		return string.join(xml, '\n')
		
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
		l1 = string.split(path, os.sep)
		for key in self.tree.keys():
			l2 = string.split(key, os.sep)
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
			if os.path.isdir(filepath) and not \
			os.path.islink(filepath):
				self.build(os.path.join(dir, f))
			else:
				if re.match('.*\.rpm$', f) != None:
					v.append(RPMFile(filepath))
				elif re.match('roll-.*\.iso$', f) != None:
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

	def getSize(self):
		'Return the size the if Tree in Mbytes'

		len = 0
		for key in self.tree.keys():
			for file in self.tree[key]:
				len = len + file.getSize()
		return float(len)
    

	def __dumpIter__(self, path, file, root):
		print(path, end=' ')
		file.dump()
	
	

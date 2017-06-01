#! /opt/stack/bin/python
# 
# @SI_Copyright@
#                               stacki.com
#                                  v4.0
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


import os
import os.path
import string
import stack.file

class Media:

	def mounted(self):
		"Returns true if the /mnt/cdrom device is mounted"

		rv = 0
		f = open('/proc/mounts','r')
		for line in f:
			if '/mnt/cdrom' in line:
				rv = 1
				break
		f.close()
		return rv


	def mountCD(self, prefix="/"):
		"""Try to mount the CD. Returns 256 if mount failed
		(no disk in drive), 0 on success."""

		if self.mounted():
			return 1
			
		mountpoint = os.path.join(prefix, 'mnt', 'cdrom')

		#
		# loader creates '/tmp/stack-cdrom' -- the cdrom device
		#
		rc = os.system('mount -o ro /tmp/stack-cdrom'
			+ ' %s > /dev/null 2>&1' % (mountpoint))

		return rc


	def umountCD(self, prefix="/"):
		if not self.mounted():
			return
              
		mountpoint = os.path.join(prefix, 'mnt', 'cdrom')
		os.system('umount %s > /dev/null 2>&1' % (mountpoint))
                return


	def ejectCD(self):
		self.umountCD()

		#
		# there are cases where the CD doesn't immediately un-mount
		# (it could be a slow finishing operation).
		#
		# try 10 times to unmount the CD.
		#
		i = 0
		while self.mounted() and i < 10:
			self.umountCD()
			i += 1

		#
		# the 'eject' utility requires '/etc/fstab' to exist
		#
		os.system('touch /etc/fstab')

		#
		# loader creates the cdrom device '/tmp/stack-cdrom'
		#
		cmd = '/usr/sbin/eject /tmp/stack-cdrom '
		cmd += '> /dev/null 2>&1'
		os.system(cmd)

		return


	def getCDInfo(self):
		self.mountCD()

		timestamp = None
		name = None
		archinfo = None
		diskid = None
		vers = None
		release = None

		if os.path.exists('/mnt/cdrom/.treeinfo'):
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
					elif value == 'CentOS':
						name = 'CentOS'
					elif value == 'Oracle Linux Server':
						name = 'Oracle'
				elif key == 'version':
					vers = value
				elif key == 'arch':
					archinfo = value
				elif key == 'discnum':
					diskid = value
			file.close()

		try:
			file = open('/mnt/cdrom/.discinfo', 'r')
			t = file.readline()
			n = file.readline()
			a = file.readline()
			d = file.readline()
			file.close()

			timestamp = t[:-1]
			
			if not name:
				name = n[:-1].replace(' ', '_')
			if not archinfo:
				archinfo = a[:-1]

			#
			# always get the disk id
			# if there are multiple disks, this will be 1, 2, etc.
			#
			# the diskid from .treeinfo appears to be hardcoded to
			# 1 (at least for CentOS media).
			#
			diskid = d[:-1]
		except:
			pass

		if not name:
			name = "BaseOS"
		if not archinfo:
			archinfo = 'x86_64'

		return (timestamp, name, archinfo, diskid, vers)


	def getId(self):
		"""Get the Id of the physical roll CD."""

		(timestamp, name, archinfo, diskid, version) = self.getCDInfo()

		if name != None and diskid != None:
			str = '%s - Disk %s' % (name, diskid)
		else:
			str = 'Not Identified'

		return str
		

	def getRollsFromCD(self):
		import re

		roll_list = []
		self.mountCD()
		regexp = re.compile('roll-.*.xml')
		for r,d,f in os.walk('/mnt/cdrom'):
			for fname in f:
				if regexp.match(fname):
					xmlfile = stack.file.RollInfoFile(
						'%s/%s' % (r, fname))
					rollname = xmlfile.getRollName()
					rollversion = xmlfile.getRollVersion()
					rollrelease = xmlfile.getRollRelease()
					rollarch = xmlfile.getRollArch()

					if not rollname:
						continue
					if not rollversion:
						continue
					if not rollrelease:
						continue
					if not rollarch:
						continue

					roll_list.append((rollname, rollversion,
						rollrelease, rollarch))

		return roll_list
				

	def listRolls(self, url, diskid, rollList):
		if os.path.exists('/tmp/updates/stack/bin/wget'):
			wget = '/tmp/updates/stack/bin/wget'
		else:
			wget = '/usr/bin/wget'

		cmd = "%s --timeout=15 --tries=2 -O - -nv %s 2>&1 " % \
			(wget, url)

		for line in os.popen(cmd).readlines():
			l = string.split(line, '"')

			if l[0] == '<a href=':
				#
				# apache style listing
				#
				filename = l[1]
			elif len(l) > 2 and l[2] == '><a href=':
				#
				# lighttpd style listing
				#
				filename = l[3]
			else:
				continue
				
			if len(filename) > 0 and filename[-1] == '/':
				#
				# this is a directory
				#
				dir = filename[:-1]
				
				if dir in [ '.', '..']:
					continue

				# Support old style and new style rolls
				# OLD: <name>/<version>/<arch>/RedHat
				# NEW: <name>/<version>/redhat/<arch>

				urlList = url.split('/')
				
				if len(urlList) >= 4 and urlList[-1] == 'redhat':
					n = urlList[-3]
					v = urlList[-2]
					a = dir
					rollList.append((n, v, a, diskid))
				elif len(urlList) >= 4 and dir == 'RedHat':
					n = urlList[-3]
					v = urlList[-2]
					a = urlList[-1]
					rollList.append((n, v, a, diskid))
				else:
					self.listRolls(os.path.join(url, dir),
					       diskid, rollList)



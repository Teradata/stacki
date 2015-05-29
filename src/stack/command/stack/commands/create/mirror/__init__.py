# @SI_Copyright@
#                             www.stacki.com
#                                  v1.0
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
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
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
import stat
import time
import sys
import string
import subprocess
import shlex
import stack
import stack.commands


class Command(stack.commands.create.command):
	"""	
	Create a pallet ISO image from the packages found in the
	repository located at 'URL'.

	Mirroring RHEL repositories works with a subscribed Red Hat frontend.
	Direct access via a url, will not work.

	All other public repositories can use a repoid or url.

	If using a url, "newest" and "urlonly" have no effect. The entire
	distribution will be downloaded.

	<arg type='string' name='path'>	
	The network location of the repository of packages.
	</arg>
	
	<param type='string' name='name'>
	The base name for the created pallet. If "repoid" is specified, then
	the base name of the pallet will be the repoid, otherwise the base name
	of the pallet will be 'updates'.
	</param>
	
	<param type='string' name='version'>
	The version number of the created pallet. (default = the version of 
	Rocks running on this machine).
	</param>

	<param type='string' name='arch'>
	Architecture of the mirror. (default = the architecture of 
	of the OS running on this machine).
	</param>

	<param type='string' name='repoid' optional='1'>
	The repoid to mirror. Repoid's are found by executing: "yum repolist".
	Default: None.
	</param>

	<param type='string' name='repoconfig' optional='1'>
	The path to a repo configuration file. Default: None.
	</param>

	<param type='boolean' name='newest' optional='1'>
	Get only the latest RPMS from the repo. Default is "no"
	and downloads the entire set of RPMS from the distribution.
	</param>

	<param type='boolean' name='urlonly' optional='1'>	
	Print only the list of RPMS in the repo to be downloaded. 
	Useful for checking what will be downloaded.
	Default is "no."
	</param>

	<example cmd='create mirror http://mirrors.kernel.org/centos/6.5/updates/x86_64/Packages name=updates version=6.5'>
	Creates a mirror for CentOS 6.5 based on the packages from mirrors.kernel.org.
	The pallet ISO will be named 'updates-6.5-0.x86_64.disk1.iso'.
	</example>

	<example cmd='create mirror repoid=rhel-6-server-rpms newest=yes version=6.5'>
	Creates a mirror for RHEL 6.5 based on the latest packages from cdn.redhat.com.
	The pallet ISO will be named rhel-6-server-rpms-6.5-0.x86_64.disk1.iso.
	</example>
	"""

	def mirror(self, mirror_path):
		cmd = 'wget -erobots=off --reject "*.drpm" '
		cmd += '--reject "anaconda*rpm" -m -nv -np %s' % (mirror_path)
		proc = subprocess.Popen(shlex.split(cmd), stdin = None,
			stdout = subprocess.PIPE, stderr = subprocess.PIPE)
		o, e = proc.communicate()

		if len(mirror_path) > 6:
			if mirror_path[0:6] == 'ftp://':
				mirrordir = mirror_path[6:]
			elif mirror_path[0:7] == 'http://':
				mirrordir = mirror_path[7:]
			else:
				mirrordir = mirror_path

		os.symlink(mirrordir, 'RPMS')

	def repoquery(self,repoid, repoconfig):
		cmd = 'repoquery -qa --repoid=%s' % repoid

		if repoconfig:
			cmd = cmd + ' --config=%s' % repoconfig

		proc = subprocess.Popen(shlex.split(cmd), stdin = None,
			stdout = subprocess.PIPE, stderr = subprocess.PIPE)
		o,e = proc.communicate()
		return o,e

	def reposync(self, repoid, repoconfig, newest, urlonly):
		cmd = 'reposync --norepopath -r %s -p %s' % (repoid, repoid)

		if repoconfig:
			cmd += ' -c %s' % repoconfig

		if self.str2bool(newest) == True:
			cmd += ' -n'

		if self.str2bool(urlonly) == True:
			cmd += ' -u'
			proc = subprocess.Popen(shlex.split(cmd), stdin = None,
				stdout = subprocess.PIPE, stderr = subprocess.PIPE)
			o,e = proc.communicate()
			return o,e
		else:
			proc = subprocess.Popen(shlex.split(cmd), stdin = None,
				stdout = subprocess.PIPE, stderr = subprocess.PIPE)
			o, e = proc.communicate()

		if repoid and (self.str2bool(urlonly) == False):
			cwd = os.getcwd()
			os.chdir(repoid)
			# Check if RPMS dir already exists
			if not os.path.lexists('RPMS'):
				os.symlink('.', 'RPMS')
			os.chdir(cwd)


	def makeRollXML(self, name, version, arch, xmlfilename):
		file = open(xmlfilename, 'w')
		file.write('<roll name="%s" interface="6.0.2">\n' % name)

		rolltime = time.strftime('%X')
		rolldate = time.strftime('%b %d %Y')
		rollzone = time.strftime('%Z')
		file.write('\t<timestamp time="%s" date="%s" tz="%s"/>\n' %
			(rolltime, rolldate, rollzone))

		file.write('\t<color edge="lawngreen" node="lawngreen"/>\n')
		file.write('\t<info version="%s" release="0" arch="%s"/>\n' % 
			(version, arch))

		file.write('\t<iso maxsize="0" bootable="0" mkisofs=""/>\n')
		file.write('\t<rpm rolls="0" bin="1" src="0"/>/\n')
		file.write('</roll>\n')
		file.close()


	def clean(self):
		if os.path.islink('RPMS'):
			os.unlink('RPMS')
		os.system('rm -rf disk1')


	def run(self, params, args):
		try:
			version = stack.version
		except AttributeError:
			version = 'X'
			
		(name, version, arch, repoid, repoconfig, 
			newest, urlonly) = self.fillParams(
			[('name', None),
			('version', version),
			('arch', self.arch), 
			('repoid', None),
			('repoconfig', None),
			('newest', 'no'),
			('urlonly', 'no')])

		# Any call to reposync creates a directory
		# We don't want that if urlstatus is True.
		# So check it's value for T/F.
		# Hence all the "if urlstatus == False" in the
		# following code.
		urlstatus = self.str2bool(urlonly)

		mirror_path = None
		if len(args) == 1:
			mirror_path = args[0]

		if name == None:
			if repoid:
				name = repoid
			else:
				name = 'updates'

		if not repoid and not mirror_path:
			self.abort('must supply a URL argument or a "repoid"')

		# Query the repo to see if it exists and we can get to it.
		rpms,repoerr = self.repoquery(repoid, repoconfig)
		if repoerr and rpms == 'None' and not mirror_path:
			msg =  "I do not think this repoid "
			msg += "means what you think "
			msg += "it means. "
			msg += "\n\nrepoid '%s' doesn't " % repoid
			msg += "appear to be a valid repo.\n"
			self.abort(msg)

		# If urlonly, just print what will be downloaded.
		if urlstatus  == True:
			rpms, err = self.reposync(repoid,repoconfig,newest,urlonly)
			print rpms
			os.system('rm -fr %s' % repoid)

		cwd = os.getcwd()

		if repoid and (urlstatus == False):
			if not os.path.exists(repoid):
				os.makedirs(repoid)	
			os.chdir(repoid)
			self.clean()
			os.chdir(cwd)
		else:
			self.clean()
		
		if mirror_path:
			self.mirror(mirror_path)
		elif repoid and urlstatus == False:
			self.reposync(repoid, repoconfig, newest, urlonly)

		if repoid and (urlstatus == False):
			os.chdir(repoid)

		if urlstatus:
			pass
		else:
			xmlfilename = 'roll-%s.xml' % name
			self.makeRollXML(name, version, arch, xmlfilename)
			self.command('create.pallet', [ '%s' % (xmlfilename) ] )
		
		self.clean()

		if repoid and (urlstatus == False):
			os.chdir(cwd)

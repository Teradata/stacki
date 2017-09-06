# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@

from __future__ import print_function
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
from stack.exception import *


class Command(stack.commands.create.command):
	"""	
	Create a pallet ISO image from the packages found in the
	repository located at 'URL'.

	Mirroring RHEL repositories works with a subscribed Red Hat frontend.
	Direct access via a url, will not work.

	All other public repositories can use a repoid or url.

	If using a url, "newest" and "urlonly" have no effect. The entire
	repo will be downloaded.

	<param type='string' name='url'>	
	The location of the repository of packages to mirror.  Can be an 
	http(s) or ftp URL, or a local path.
	</param>
	
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

	<param type='string' name='repoid'>
	The repoid to mirror. Repoid's are found by executing: "yum repolist".
	Default: None.
	</param>

	<param type='string' name='repoconfig'>
	The path to a repo configuration file. Default: None.
	</param>

	<param type='boolean' name='newest'>
	Get only the latest RPMS from the repo. Default is "True"
	and downloads only the most recent versions of the RPMs
	in the repo.
	
	Set to "false" or "no" to get all versions of the RPMs
	in a repository.
	</param>

	<param type='boolean' name='urlonly'>	
	Print only the list of RPMS in the repo to be downloaded. 
	Useful for checking what will be downloaded.
	Default is "no."
	</param>

	<example cmd='create mirror url=http://mirrors.kernel.org/centos/6.5/updates/x86_64/Packages name=updates version=6.5'>
	Creates a mirror for CentOS 6.5 based on the packages from mirrors.kernel.org.
	The pallet ISO will be named 'updates-6.5-0.x86_64.disk1.iso'.
	</example>

	<example cmd='create mirror repoid=rhel-6-server-rpms newest=yes version=6.5'>
	Creates a mirror for RHEL 6.5 based on the latest packages from cdn.redhat.com.
	The pallet ISO will be named rhel-6-server-rpms-6.5-0.x86_64.disk1.iso.
	</example>

	<example cmd='create mirror url=/tmp/ansible_deps name=ansible version=4.0'>
	Creates a pallet based on packages already collected in /tmp/ansible_deps
	to install Ansible with dependencies.
	The pallet ISO will be named ansible-4.0-7.x.x86_64.disk1.iso
	</example>
	"""

	def mirror(self, mirror_url):
		try:
			scheme, url = mirror_url.split('://')
		except ValueError:
			# If there is no scheme, mirror_url is just a local file
			scheme = None
			url = mirror_url

		# wget doesn't support the file:// scheme, but we'll just use the symlink
		if scheme == 'file':
			scheme = None

		# wget only supports http(s) and ftp
		if scheme and scheme not in ('http', 'ftp', 'https'):
			msg = "'%s' is not supported in 'stack create mirror'" % scheme
			raise CommandError(self, msg)

		# use wget to do the mirroring.
		if scheme:
			cmd = 'wget -erobots=off --reject "*.drpm" --reject "anaconda*rpm" '
			cmd += ' --mirror --no-verbose --no-parent %s' % (scheme + '://' + url)
			proc = subprocess.Popen(shlex.split(cmd), stdin = None,
				stdout = subprocess.PIPE, stderr = subprocess.PIPE)
			o, e = proc.communicate()

		# finally, symlink the directory to RPM's
		os.symlink(url, 'RPMS')

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


	def makeRollXML(self, name, version, release, arch, xmlfilename):
		file = open(xmlfilename, 'w')
		file.write('<roll name="%s" interface="3.1">\n' % name)

		rolltime = time.strftime('%X')
		rolldate = time.strftime('%b %d %Y')
		rollzone = time.strftime('%Z')
		file.write('\t<timestamp time="%s" date="%s" tz="%s"/>\n' %
			(rolltime, rolldate, rollzone))

		file.write('\t<color edge="lawngreen" node="lawngreen"/>\n')
		file.write('\t<info version="%s" release="%s" arch="%s"/>\n' %
			(version, release, arch))

		file.write('\t<iso maxsize="0" addcomps="0" bootable="0" mkisofs=""/>\n')
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

		try:
			release = stack.release
		except AttributeError:
			release = 0
			
		(url, name, version, release, arch, repoid, repoconfig, newest, urlonly) = self.fillParams([
			('url', None),
			('name', None),
			('version', version),
			('release', release),
			('arch', self.arch), 
			('repoid', None),
			('repoconfig', None),
			('newest', 'yes'),
			('urlonly', 'no')
			])

		# Any call to reposync creates a directory
		# We don't want that if urlstatus is True.
		# So check it's value for T/F.
		# Hence all the "if urlstatus == False" in the
		# following code.
		urlstatus = self.str2bool(urlonly)

		if name == None:
			if repoid:
				name = repoid
			else:
				name = 'updates'

		if not repoid and not url:
			raise ParamRequired(self, ('url', 'repoid'))

		# Query the repo to see if it exists and we can get to it.
		rpms,repoerr = self.repoquery(repoid, repoconfig)
		if repoerr and rpms == 'None' and not url:
			msg =  "I do not think this repoid "
			msg += "means what you think "
			msg += "it means. "
			msg += "\n\nrepoid '%s' doesn't " % repoid
			msg += "appear to be a valid repo.\n"
			raise CommandError(self, msg)

		# If urlonly, just print what will be downloaded.
		if urlstatus  == True:
			rpms, err = self.reposync(repoid,repoconfig,newest,urlonly)
			print(rpms)
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
		
		if url:
			self.mirror(url)
		elif repoid and urlstatus == False:
			self.reposync(repoid, repoconfig, newest, urlonly)

		if repoid and (urlstatus == False):
			os.chdir(repoid)

		if urlstatus:
			pass
		else:
			xmlfilename = 'roll-%s.xml' % name
			self.makeRollXML(name, version, release, arch, xmlfilename)
			self.command('create.pallet', [ '%s' % (xmlfilename), 'newest=%s' % newest] )
		
		self.clean()

		if repoid and (urlstatus == False):
			os.chdir(cwd)

# @SI_Copyright@
#                             www.stacki.com
#                                  v2.0
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
import os
import sys
import re
import string
import stat
import time
import tempfile
import shutil
import popen2
import pexpect
import socket
import subprocess
import shlex
import stack
import stack.commands
import stack.dist
import stack.file
import stack.roll
import stack.util
from stack.exception import *


class Builder:

	def __init__(self):
		self.config = None
		self.tempdir = os.getcwd()

	def mktemp(self):
		return tempfile.mktemp(dir=self.tempdir)
		
	def makeBootable(self, name):
		pass
				
	def mkisofs(self, isoName, rollName, diskName, rollDir):
		print('Building ISO image for %s ...' % diskName)

		if self.config.isBootable():
			extraflags = self.config.getISOFlags()
		else:
			extraflags = ''

		volname = '%s %s' % (rollName, diskName)
		if len(volname) > 32:
			volname = volname[0:32]
			
		cwd = os.getcwd()
		cmd = 'mkisofs -V "%s" %s -r -T -f -o %s .' % \
			(volname, extraflags, os.path.join(cwd, isoName))

		os.chdir(rollDir)
		subprocess.call(shlex.split(cmd), stdin = None, stdout = None,
			stderr = None)

		if self.config.isBootable():
			subprocess.call([ 'isohybrid',
				os.path.join(cwd, isoName) ])
		os.chdir(cwd)

		
	def writerepo(self, name, version, arch):
		print('Writing repo data')
		cwd = os.getcwd()
		palletdir = os.path.join(os.getcwd(), 'disk1', name, version,
			'redhat', arch)
		os.chdir(palletdir)
		subprocess.call([ 'createrepo', '.' ])
		os.chdir(cwd)


	def copyXMLs(self, name, version, arch):
		print 'Copying graph and node XML files'

		cwd = os.getcwd()
		srcdir = os.path.join(cwd, '..')
		destdir = os.path.join(cwd, 'disk1', name, version,
			'redhat', arch)

		os.chdir(destdir)
		shutil.copytree(os.path.join(srcdir, 'graph'),
			os.path.join(destdir, 'graph'))
		shutil.copytree(os.path.join(srcdir, 'nodes'),
			os.path.join(destdir, 'nodes'))
		os.chdir(cwd)

		
	def copyFile(self, path, file, root):
		if file.getName() in [ 'TRANS.TBL' ]:
			return

		dir	 = os.path.join(root, path)
		fullname = os.path.join(dir, file.getName())
		if not os.path.isdir(dir):
			os.makedirs(dir)

		shutil.copy(file.getFullName(), fullname)
		os.utime(fullname, (file.getTimestamp(), file.getTimestamp()))


	def copyRoll(self, roll, dir):
		if roll.isRollForeign():
			self.command('add.pallet', [ roll.getFullName(),
				'dir=%s' % dir, 'updatedb=n' ])
		else:
			tmp = self.mktemp()
			os.makedirs(tmp)
			os.system('mount -o loop -t iso9660 %s %s' %
				  (roll.getFullName(), tmp))
			tree = stack.file.Tree(tmp)
			tree.apply(self.copyFile, dir)
			os.system('umount %s' % tmp)
			shutil.rmtree(tmp)


	def stampDisk(self, dir, name, arch, id=1):
		file = os.path.join(dir, '.discinfo')
		if os.path.isfile(file):
			os.unlink(file)
		fout = open(file, 'w')
		fout.write('%f\n' % time.time())
		fout.write('%s\n' % name)
		fout.write('%s\n' % arch)
		fout.write('%d\n' % id)
		fout.close()
			


class RollBuilder_redhat(Builder, stack.dist.Arch):

	def __init__(self, file, command, call):
		Builder.__init__(self)
		stack.dist.Arch.__init__(self)
		self.config = stack.file.RollInfoFile(file)
		self.setArch(self.config.getRollArch())
		self.command = command
		self.call = call

	def mkisofs(self, isoName, rollName, diskName):
		Builder.mkisofs(self, isoName, rollName, diskName, diskName)
		
	def signRPM(self, rpm):
	
		# Only sign RPMs that were build on this host.  This
		# allows pallets to include 3rd party RPMs that will
		# not be signed by the pallet builder.
		
		cmd = "rpm -q --qf '%%{BUILDHOST}' -p %s" % rpm.getFullName()
		buildhost = os.popen(cmd).readline()
		hostname  = socket.gethostname()
		
		if buildhost == hostname:
			cmd = 'rpm --resign %s' % rpm.getFullName()
			try:		
				child = pexpect.spawn(cmd)
				child.expect('phrase: ')
				child.sendline()
				child.expect(pexpect.EOF)
				child.close()
			except:
				pass
			os.system("rpm -qp %s --qf " 
				"'%%{name}-%%{version}-%%{release}: "
				"%%{sigmd5}\n'"
				% rpm.getFullName())
		

	def getRPMS(self, path):
		"""Return a list of all the RPMs in the given path, if multiple
		versions of a package are found only the most recent one will
		be included"""
		
		dict = {}
		tree = stack.file.Tree(os.path.join(os.getcwd(), path))
		for dir in tree.getDirs():
			for file in tree.getFiles(dir):
				try:
					file.getPackageName()
				except AttributeError:
					continue # skip all non-rpm files
					
				# Skip RPMS for other architecures
				
				if file.getPackageArch() not in self.getCPUs():
					continue
					
				# Resolve package versions
				if newest == True:		
					name = file.getUniqueName()
				else:
					name = file.getFullName()

				if name not in dict or file >= dict[name]:
					dict[name] = file
					
		# convert the dictionary to a list and return all the RPMFiles
		
		list = []
		for e in dict.keys():
			list.append(dict[e])
		return list


	def spanDisks(self, files, disks=[]):
		"""Given the pallet RPMS and compute the size
		of all the files and return a list of files for each disk of 
		the pallet.  The intention is for almost all pallets to be one
		CD but for our OS pallet this is not the case."""
		
		# Set the pallet size to 0 to bypass the disk spanning
		# logic.  The updates pallet does this.
		
		avail = self.config.getISOMaxSize()
		if avail <= 0:
			infinite = 1
		else:
			infinite = 0
		consumed = []
		remaining = []
		
		# Fill the CDs
		
		for file in files:
			if file and infinite:
				consumed.append(file)
			elif file and (avail - file.getSize()) > 0:
				consumed.append(file)
				avail -= file.getSize()
			else:
				remaining.append(file)
		
		id	= len(disks) + 1
		name	= 'disk%d' % id
		size	= self.config.getISOMaxSize() - avail
		disks.append((name, id, size, consumed))
		if len(remaining):
			self.spanDisks(remaining, disks)
		return disks
		

	def getExternalRPMS(self):
		import stack.roll
		import stack.gen

		# The default-all distribution includes all of the
		# installed pallets on the system and is used to generate a
		# kickstart files for the everything appliance. This gives us
		# a list of RPMs that we know we need from the source
		# os/updates CDs.

		cwd = os.getcwd()

		print('making default-all')

		self.command('create.distribution', [ 'default-all',
			'inplace=true', 'resolve=true', 'md5=false' ])

		#
		# copy the 'everything' node and graph file into the distribution
		#
		basedir = os.path.join('default-all', self.arch, 'build')
		xml = self.command('list.node.xml', [ 'everything',
			'basedir=%s' % basedir, 'eval=n' ] )

		os.chdir(cwd)

		#
		# make sure the XML string is ASCII and not unicode, 
		# otherwise, the parser will fail
		#
		xmlinput = xml.encode('ascii', 'ignore')

		generator = stack.gen.Generator_redhat()
		generator.setArch(self.arch)
		generator.setOS('redhat')
		generator.parse(xmlinput)

		rpms = []
		for line in generator.generate('packages'):
			if len(line) and line[0] not in [ '#', '%' ]:
				rpms.append(line)

		# The default-os distribution includes just the source
		# os/update CDs (already in pallet form).
		# The default-all distribution is
		# still used for the comps file and the anaconda source 
		# code.  We need this since anaconda and comps are missing
		# from the foreign pallets (os/update CDs).

		print('making default-os')

		self.command('create.distribution', [ 'default-os',
			'inplace=true', 'resolve=true', 'md5=false' ])

		#
		# make sure a comps.xml file is present
		#
		comps = os.path.join('default-os', self.arch, 'RedHat',
			'base', 'comps.xml')
		if not os.path.exists(comps):
			print('\n\tCould not find a comps.xml file.')
			print('\tCopy a comps.xml file into the CentOS pallet\n')
			sys.exit(-1)

		#
		# use yum to resolve dependencies
		#
		if stack.release == '7.x':
			pythonver = '2.7'
		else:
			pythonver = '2.6'

		sys.path.append('/usr/lib/python%s/site-packages' % pythonver)
		sys.path.append('/usr/lib64/python%s/site-packages' % pythonver)
		sys.path.append('/usr/lib/python%s/lib-dynload' % pythonver)
		sys.path.append('/usr/lib64/python%s/lib-dynload' % pythonver)

		import yum

		#
		# need to create a repo here because the 'md5=false' flag above
		# does not call createrepo and we need it below for yum to work
		#
		os.system('/usr/share/createrepo/genpkgmetadata.py ' +
			'--groupfile RedHat/base/comps.xml ' +
			'default-os/%s' % self.arch)

		a = yum.YumBase()
		a.doConfigSetup(fn='%s' % os.path.join(cwd, 'BUILD',
			'roll-%s-%s' % (self.config.getRollName(),
			self.config.getRollVersion()), 'yum.conf'),
			init_plugins=False)
		a.conf.cache = 0
		a.doTsSetup()
		a.doRepoSetup()
		a.doRpmDBSetup()
		a.doSackSetup()
		a.doGroupSetup()

		selected = []
		for rpm in rpms + [ '@base', '@core' ]:
			if rpm[0] == '@':
				group = a.comps.return_group(
					rpm[1:].encode('utf-8'))

				for r in group.mandatory_packages.keys() + \
						group.default_packages.keys():
					if r not in selected:
						selected.append(r)
			elif rpm not in selected:
				selected.append(rpm)

		pkgs = []
		avail = a.pkgSack.returnNewestByNameArch()
		for p in avail:
			if p.name in selected:
				pkgs.append(p)

		done = 0
		while not done:
			done = 1
			results = a.findDeps(pkgs)
			for pkg in results.keys():
				for req in results[pkg].keys():
					reqlist = results[pkg][req]
					for r in reqlist:
						if r.name not in selected:
							selected.append(r.name)
							pkgs.append(r)
							done = 0

		# Now build a list of rocks (required) and non-rocks (optional)
		# rpms and return both of these list.  When the ISOs are created
		# all the required packages are first.
		
		tree = stack.file.Tree(os.path.join(os.getcwd(),
			'default-os', self.arch))

		stack = []
		nonstack = []
		for rpm in tree.getFiles(os.path.join('RedHat', 'RPMS')):
			if rpm.getBaseName() in selected:
				stack.append(rpm)
			else:
				nonstack.append(rpm)

		return (stack, nonstack)


	def makeBootable(self, name):
		import stack.roll
		import stack.bootable
		import stack

		print 'Configuring pallet to be bootable ... ', name

		#
		# get 'stacki' pallet info
		#
		stacki_name = 'stacki'
		stacki_version = None
		stacki_arch = None
		for o in self.call('list.pallet', [ 'stacki' ]):
			if stack.release == o['release']:
				stacki_version = o['version']
				stacki_arch = o['arch']
				break

		# 
		# create a minimal kickstart file. this will get us to the
		# stacki wizard
		# 
		fout = open(os.path.join('disk1', 'ks.cfg'), 'w')

		if stack.release == '7.x':
			fout.write('install\n')
			fout.write('url --url http://127.0.0.1/mnt/cdrom\n')
			fout.write('lang en_US\n')
			fout.write('keyboard us\n')
		else:
			distdir = os.path.join('mnt', 'cdrom', stacki_name,
				stacki_version, 'redhat', stacki_arch)

			fout.write('install\n')
			fout.write('url --url http://127.0.0.1/%s\n' % distdir)
			fout.write('lang en_US\n')
			fout.write('keyboard us\n')
			fout.write('interactive\n')

		fout.close()

		#
		# add isolinux files
		# 
		localrolldir = os.path.join(self.config.getRollName(), 
			self.config.getRollVersion(), 'redhat', 
			self.config.getRollArch())

		destination = os.path.join(os.getcwd(), 'disk1')
		rolldir = os.path.join(destination, localrolldir)
		self.boot = stack.bootable.Bootable(os.getcwd(), rolldir)

		self.boot.installBootfiles(destination)
		
		return


	def run(self):

		# Make a list of all the files that we need to copy onto the
		# pallets cds.  Don't worry about what the file types are right
		# now, we can figure that out later.
			
		list = []
		if self.config.hasRPMS():
			list.extend(self.getRPMS('RPMS'))
		for rpm in list:
			self.signRPM(rpm)

		# Make a list of both required and optional packages.  The copy
		# code is here since python is by-reference for everything.
		# After we segregate the packages add
		# any local rpms to the required list.  This makes sure we
		# pick up the roll-os-kickstart package.
		
		required = []
		if self.config.hasRolls():
			(required, optional) = self.getExternalRPMS()
			for file in list:
				required.append(file)
			print('Required Packages', len(required))
			print('Optional Packages', len(optional))
			for file in required: # make a copy of the list
				list.append(file)
			list.extend(optional)


		optional = 0
		for (name, id, size, files) in self.spanDisks(list):
			print('Creating %s (%.2fMB)...' % (name, size), end=' ')
			if optional:
				print(' This disk is optional (extra rpms)')
			else:
				print() 
				
			if self.config.getRollInterface() == '4.0':
				# old style
				root = os.path.join(name,
						    self.config.getRollName(),
						    self.config.getRollVersion(),
						    self.config.getRollArch())
				rpmsdir = os.path.join('RedHat', 'RPMS')
			else:
				root = os.path.join(name,
						    self.config.getRollName(),
						    self.config.getRollVersion(),
						    'redhat',
						    self.config.getRollArch())

				rpmsdir = 'RPMS'

			os.makedirs(root)
			os.makedirs(os.path.join(root, rpmsdir))
			
			# Symlink in all the RPMS
			
			for file in files:
				try:
					#
					# not RPM files will throw an exception
					# in getPackageArch()
					#
					arch = file.getPackageArch()
				except:
					continue

				if arch != 'src':
					file.symlink(
						os.path.join(root, rpmsdir,
							     file.getName()))
				if file in required:
					del required[required.index(file)]
					
			if len(required) == 0:
				optional = 1
				
			# Copy the pallet XML file onto all the disks
			shutil.copy(self.config.getFullName(), root)
			
			# Create the .discinfo file
					
			self.stampDisk(name, self.config.getRollName(), 
				self.config.getRollArch(), id)
				
			# write repodata 
			self.writerepo(self.config.getRollName(),
				self.config.getRollVersion(),
				self.config.getRollArch())

			# copy the graph and node XMLs files into the pallet
			self.copyXMLs(self.config.getRollName(),
				self.config.getRollVersion(),
				self.config.getRollArch())
			
			# make the ISO.  This code will change and move into
			# the base class, and supported bootable pallets.  Get
			# this working here and then test on the bootable
			# kernel pallet.
			
			isoname = '%s-%s-%s.%s.%s.iso' % (
				self.config.getRollName(),
				self.config.getRollVersion(),
				self.config.getRollRelease(),
				self.config.getRollArch(),
				name)
				
			if id == 1 and self.config.isBootable() == 1:
				self.makeBootable(name)
			
			self.mkisofs(isoname, self.config.getRollName(), name)


		
class MetaRollBuilder(Builder):

	def __init__(self, files, rollname, version, command):
		self.version = version.strip()
		self.rollname = rollname
		self.command = command

		Builder.__init__(self)

		self.rolls = []

		for file in files:
			try:
				self.rolls.append(stack.file.RollFile(file))
			except OSError:
				print('error - %s, no such pallet' % file)
				sys.exit(-1)

	def run(self):
	
		name = []
		arch = []
		for roll in self.rolls:
			if roll.getRollName() not in name:
				name.append(roll.getRollName())
			if roll.getRollArch() not in arch:
				arch.append(roll.getRollArch())

		if not self.rollname:
			name.sort()
			rollName = string.join(name, '+')
		else:
			rollName = self.rollname
	
		if len(arch) == 1:
			arch = arch[0]
		else:
			arch = 'any'
		name = "%s-%s.%s" % (rollName, self.version, arch)

    		# Create the meta pallet
					
		print('Building %s ...' % name)
		tmp = self.mktemp()
		os.makedirs(tmp)
		for roll in self.rolls:
			print('\tcopying %s' % roll.getRollName())
			self.copyRoll(roll, tmp)
		isoname = '%s.disk1.iso' % (name)

		# Find a pallet config file for the meta pallet. If any of
		# the pallets are bootable grab the config file for the
		# bootable pallet.  Otherwise just use the file from
		# the first pallet specified on the command line.

		for roll in self.rolls:
			xml = os.path.join(tmp, roll.getRollName(), 
				roll.getRollVersionString(), 
				'redhat',
				roll.getRollArch(),
				'roll-%s.xml' % roll.getRollName())
			
			if not os.path.exists(xml):
				xml = os.path.join(tmp,
					roll.getRollName(),
					roll.getRollVersionString(),
					roll.getRollArch(),
					'roll-%s.xml' % roll.getRollName())

			config = stack.file.RollInfoFile(xml)
			if not self.config:
				self.config = config
			elif config.isBootable():
				self.config = config
				break

		# Build the ISO.
		
		tree = stack.file.Tree(tmp)
		size = tree.getSize()
		print('Pallet is %.1fMB' % size)

		self.stampDisk(tmp, rollName, arch)
		self.mkisofs(isoname, rollName, 'disk1', tmp)

		shutil.rmtree(tmp)


class Command(stack.commands.create.command,
		stack.commands.HostArgumentProcessor):

	"""
	Create a pallet.  You may specify either a single XML file to build
	one pallet or a list of ISO files to build a Meta pallet.

	<arg type='string' name="pallet" repeat='1'>
	Either a list of pallet ISO files or the name of a single pallet XML
	description file.  If a list of pallet ISO files to be merge together 
	into a single pallet.  Otherwise the single argument is assumed to
	be the name of the XML file generated by the top level Makefile in
	the pallet's source.
	</arg>

	<param type='string' name='name'>
	The base name for the created pallet.
	</param>
	
	<param type='string' name='version'>
	The version number of the created pallet. (default = the version of 
	stacki running on this machine).
	</param>

	<param type='boolean' name='newest'>
	</param>

	<example cmd='create pallet pallet-base.xml'>
	Creates the Rocks Base pallet from the pallet-base.xml description file.
	</example>
	
	<example cmd='create pallet base*iso kernel*iso'>
	Create a composite pallet from a list of pallet ISOs.
	</example>

	<related>add pallet</related>
	<related>remove pallet</related>
	<related>enable pallet</related>
	<related>disable pallet</related>
	<related>list pallet</related>
	"""

	def run(self, params, args):

		try:
			version = stack.version
		except AttributeError:
			version = 'X'

		(name, version, newest) = self.fillParams([
                        ('name', None),
			('version', version),
			('newest', True) 
                        ])
		# Yes, globals are probably bad. But this is the fastest
		# to getting what we want. Otherise have to pass all this
		# in various arg lines to the defined classes and defs 
		# in this file. Blame Greg, he said it was okay.
		global newest

                if len(args) == 0:
                        raise ArgRequired(self, 'pallet')
                
		# Set pallet Builder to correct OS
		roller = getattr(stack.commands.create.pallet,
			'RollBuilder_%s' % (self.os))
		if len(args) == 1:
			base, ext = os.path.splitext(args[0])
			if ext == '.xml':
				builder = roller(args[0], self.command,
					self.call)
			else:
                                raise CommandError(self, 'missing xml file')
		elif len(args) > 1:
			for arg in args:
				base, ext = os.path.splitext(arg)
				if not ext == '.iso':
                                        raise CommandError(self, 'bad iso file')
			builder = MetaRollBuilder(args, name, version,
				self.command)
			
		builder.run()


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
import sys
import string
import time
import tempfile
import shutil
import subprocess
import shlex
import glob
import json
import stack
import stack.commands
import stack.dist
import stack.file
import stack.roll
import stack.util
import stack.bootable
from stack.exception import CommandError, ArgRequired



class Builder:

	def __init__(self):
		self.config = None
		self.tempdir = os.getcwd()

	def mktemp(self):
		return tempfile.mktemp(dir=self.tempdir)
		
	def makeBootable(self, name, version, release, arch):
		pass
				
	def mkisofs(self, isoName, rollName, diskName, rollDir):
		print('Building ISO image for %s' % diskName)

		if self.config.isBootable():
			extraflags = self.config.getISOFlags()
		else:
			extraflags = ''

		volname = "stacki"
		cwd = os.getcwd()
		cmd = 'mkisofs -quiet -V "%s" %s -r -T -f -o %s .' % \
			(volname, extraflags, os.path.join(cwd, isoName))

#		print('mkisofs: cmd %s' % cmd)
		stack.util._exec(cmd, shlexsplit=True, cwd=rollDir)

		if self.config.isBootable():
			stack.util._exec(['isohybrid', os.path.join(cwd, isoName)], cwd=rollDir)
#			subprocess.call([ 'isohybrid',
#				os.path.join(cwd, isoName) ])
#		os.chdir(cwd)

		
	def writerepo(self, name, version, release, OS, arch):
		print('Writing repo data')
		basedir = os.getcwd()
		palletdir = os.path.join(basedir, 'disk1', name, version,
			release, OS, arch)
		os.chdir(palletdir)

		subprocess.call(['createrepo', '.'])

		os.chdir(basedir)


	def copyXMLs(self, osname, name, version, release, arch):
		print('Copying graph and node XML files')

		dst = os.path.join('disk1', name, version, release, osname, arch)
		
		for xml in [ 'graph', 'nodes' ]:
			os.makedirs(os.path.join(dst, xml))
			for src in [ xml, os.path.join('..', xml) ]:
				if not os.path.exists(src):
					continue
				for filename in os.listdir(src):
					base, ext = os.path.splitext(filename)
					if ext == '.xml':
						shutil.copy(os.path.join(src, filename),
							    os.path.join(dst, xml, filename))

		
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
			os.system('mount -o loop -t iso9660 %s %s > /dev/null 2>&1' %
				  (roll.getFullName(), tmp))
			tree = stack.file.Tree(tmp)
			tree.apply(self.copyFile, dir)
			os.system('umount %s > /dev/null 2>&1' % tmp)
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
			


class RollBuilder(Builder, stack.dist.Arch):

	def __init__(self, file, command, call):
		Builder.__init__(self)
		stack.dist.Arch.__init__(self)
		self.config = stack.file.RollInfoFile(file)
		self.setArch(self.config.getRollArch())
		self.command = command
		self.call = call

	def mkisofs(self, isoName, rollName, diskName):
		Builder.mkisofs(self, isoName, rollName, diskName, diskName)
		
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
				except:
					continue # skip all non-rpm files
					
				# Skip RPMS for other architecures
				
				if file.getPackageArch() not in self.getCPUs():
					continue
					
				# Resolve package versions
				if newest is True:		
					name = file.getUniqueName()
				else:
					name = file.getFullName()

				if (name not in dict) or (file >= dict[name]):
					dict[name] = file
					
		# convert the dictionary to a list and return all the RPMFiles
		
		list = []
		for e in dict.keys():
			list.append(dict[e])
		return list


	def spanDisks(self, files, disks=[]):
		"""Given the pallet RPMS and backend the size
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
		import stack.redhat.gen

		attrs = {}
		for row in self.call('list.host.attr', [ 'localhost' ]):
			attrs[row['attr']] = row['value']
		xml = self.command('list.node.xml', [ 'everything', 'eval=n', 'attrs=%s' % attrs ] )

		#
		# make sure the XML string is ASCII and not unicode, 
		# otherwise, the parser will fail
		#
		xmlinput = xml.encode('ascii', 'ignore')

		generator = stack.redhat.gen.Generator()
		generator.setProfileType('native')
		generator.setArch(self.arch)
		generator.setOS('redhat')
		generator.parse(xmlinput)

		# call the getPackages, for just enabled packages and flatten it
		rpms = [pkg for node_pkgs in generator.packageSet.getPackages()['enabled'].values() for pkg in node_pkgs]

		# create a yum.conf file that contains only repos from the
		# default-all box
		#
		cwd = os.getcwd()
		yumconf = os.path.join(cwd, 'yum.conf')

		file = open(yumconf, 'w')

		file.write('[main]\n')
		file.write('cachedir=%s/cache\n' % cwd)
		file.write('keepcache=0\n')
		file.write('debuglevel=2\n')
		file.write('logfile=%s/yum.log\n' % cwd)
		file.write('pkgpolicy=newest\n')
		file.write('distroverpkg=os-release\n')
		file.write('tolerant=1\n')
		file.write('exactarch=1\n')
		file.write('obsoletes=1\n')
		file.write('gpgcheck=0\n')
		file.write('plugins=0\n')
		file.write('metadata_expire=1800\n')
		file.write('reposdir=%s\n' % cwd)

		for o in self.call('list.pallet', []):
			boxes = o['boxes'].split()
			if 'default-all' in boxes:
				file.write('[%s]\n' % o['name'])
				file.write('name=%s\n' % o['name'])
				file.write('baseurl=file:///export/stack/pallets/%s/%s/%s/redhat/%s\n' % (o['name'], o['version'], o['release'], o['arch']))

		file.close()

		# Use system python (2.x)
		cmd = ['/usr/bin/python', '/opt/stack/sbin/yumresolver', yumconf]
		cmd.extend(rpms)
		proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		stdout, stdrr = proc.communicate()

		try:
			selected = json.loads(stdout)
		except ValueError:
			raise CommandError(self, 'Unable to parse yum dependency resolution')

		#
		# copy all the selected files into the pallet but before we
		# do that, rewrite the yum.conf file to include only the
		# 'default-os' box which will ensure that we only put
		# os-related packages in the os pallet (otherwise, packages
		# from the 'stacki' pallet would leak into the os pallet
		#
		file = open(yumconf, 'w')

		file.write('[main]\n')
		file.write('cachedir=%s/cache\n' % cwd)
		file.write('keepcache=0\n')
		file.write('debuglevel=2\n')
		file.write('logfile=%s/yum.log\n' % cwd)
		file.write('pkgpolicy=newest\n')
		file.write('distroverpkg=os-release\n')
		file.write('tolerant=1\n')
		file.write('exactarch=1\n')
		file.write('obsoletes=1\n')
		file.write('gpgcheck=0\n')
		file.write('plugins=0\n')
		file.write('metadata_expire=1800\n')
		file.write('reposdir=%s\n' % cwd)

		for o in self.call('list.pallet', []):
			boxes = o['boxes'].split()
			if 'default-os' in boxes:
				file.write('[%s]\n' % o['name'])
				file.write('name=%s\n' % o['name'])
				file.write('baseurl=file:///export/stack/pallets/%s/%s/%s/redhat/%s\n' % (o['name'], o['version'], o['release'], o['arch']))

		file.close()
		destdir = os.path.join(cwd, 'RPMS')

		cmd = [ 'yumdownloader', '--destdir=%s' % destdir, '-y', '-c', yumconf ]
		cmd.extend(selected)
		subprocess.call(cmd, stdin=None)
		
		stacki = []
		nonstacki = []

		tree = stack.file.Tree(destdir)

		for rpm in tree.getFiles():
			if rpm.getBaseName() in selected:
				stacki.append(rpm)
			else:
				nonstacki.append(rpm)

		return (stacki, nonstacki)


	def makeBootable(self, name, version, release, arch):
		import stack.roll
		import stack

		print('Configuring pallet to be bootable ... ', name)

		# 
		# create a minimal kickstart file. this will get us to the
		# stacki wizard
		# 
		fout = open(os.path.join('disk1', 'ks.cfg'), 'w')

		palletdir = os.path.join(name,
			version, release, 'redhat', arch)
		distdir = os.path.join('mnt', 'cdrom', palletdir)
		fout.write('install\n')
		fout.write('lang en_US\n')
		fout.write('keyboard us\n')
		fout.write('interactive\n')
		if release == 'redhat7':
			fout.write('url --url cdrom:cdrom:%s\n' % palletdir)
		else:
			fout.write('url --url http://127.0.0.1/%s\n' % distdir)

		fout.close()

		# Write USB file
		if release == 'redhat7':
			fout = open(os.path.join('disk1', 'ks-usb.cfg'), 'w')
			fout.write('install\n')
			fout.write('lang en_US\n')
			fout.write('keyboard us\n')
			fout.write('interactive\n')
			fout.write('url --url hd:LABEL=stacki:%s\n' % palletdir)
			fout.close()

		#
		# add isolinux files
		# 
		localrolldir = os.path.join(name, version, release, 'redhat', arch)

		destination = os.path.join(os.getcwd(), 'disk1')
		rolldir = os.path.join(destination, localrolldir)
		self.boot = stack.bootable.Bootable(os.getcwd(), rolldir)

		self.boot.installBootfiles(destination)
		
		return


	def run(self):

		# Make a list of all the files that we need to copy onto the
		# pallets cds.	Don't worry about what the file types are right
		# now, we can figure that out later.

		list = []
		if self.config.hasRPMS():
			list.extend(self.getRPMS('RPMS'))

		# Make a list of both required and optional packages.  The copy
		# code is here since python is by-reference for everything.
		# After we segregate the packages add
		# any local rpms to the required list.	This makes sure we
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
				
			root = os.path.join(name,
					    self.config.getRollName(),
					    self.config.getRollVersion(),
					    self.config.getRollRelease(),
					    self.config.getRollOS(),
					    self.config.getRollArch())

			rpmsdir = 'RPMS'

			os.makedirs(root)
			if self.config.getRollOS() in [ 'redhat', 'sles' ]:
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
			if self.config.getRollOS() in [ 'redhat', 'sles' ]:
				self.writerepo(self.config.getRollName(),
					       self.config.getRollVersion(),
					       self.config.getRollRelease(),
					       self.config.getRollOS(),
					       self.config.getRollArch())

			# copy the graph and node XMLs files into the pallet
			self.copyXMLs(self.config.getRollOS(),
				      self.config.getRollName(),
				      self.config.getRollVersion(),
				      self.config.getRollRelease(),
				      self.config.getRollArch())
			
			# make the ISO.	 This code will change and move into
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
				try:
					self.makeBootable(self.config.getRollName(),
							  self.config.getRollVersion(),
							  self.config.getRollRelease(),
							  self.config.getRollArch())
				except ValueError as msg:
					print('ERROR -', msg)
					print('Pallet is not bootable')
					self.config.setBootable(False)

			self.mkisofs(isoname, self.config.getRollName(), name)

		
class MetaRollBuilder(Builder):

	def __init__(self, files, rollname, version, release, command):
		self.version = version.strip()
		self.rollname = rollname
		self.command = command
		self.release = release

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
			rollName = '+'.join(name)
		else:
			rollName = self.rollname
	
		if len(arch) == 1:
			arch = arch[0]
		else:
			arch = 'any'
		name = "%s-%s-%s.%s" % (rollName, self.version, self.release, arch)

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
				roll.getRollRelease(), 
				'redhat',
				roll.getRollArch(),
				'roll-%s.xml' % roll.getRollName())
			
			if not os.path.exists(xml):
				xml = os.path.join(tmp,
					roll.getRollName(),
					roll.getRollVersionString(),
					roll.getRollRelease(),
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


class GitRollBuilder(Builder):

	def __init__(self, url, commitish):
		self.url = url
		self.commitish = commitish
		self.base_dir = '/export/git_pallets/'
		self.repo_name = url.split('/')[-1].replace('.git', '')
		self.repo_full_path = self.base_dir + self.repo_name


	def run(self):
		# 1. Create landing directory
		# 2. Clone / pull source
		# 3. Checkout requested commit
		# 4. Get build environment vars
		# 5. Run 'make roll'

		self.prepare_build_dir()
		self.prepare_build_env()
		self.fetch_from_git()
		self.make_roll()


	def prepare_build_dir(self):
		# ensure base directory exists
		try:
			os.mkdir(self.base_dir)
		except OSError:
			# directory already exists
			pass


	def prepare_build_env(self):
		# set build env vars
		with open('/etc/profile.d/stack-build.sh') as build_vars_file:
			for line in build_vars_file.readlines():
				if not line.startswith('export '):
					continue

				line = line.replace('export ', '').strip()
				key, val = line.split('=')
				os.environ[key] = val


	def fetch_from_git(self):
		"""
		Fetch a pallet from a github repo, then clone and make roll
		"""

		os.chdir(self.base_dir)
		# check if the source dir already exists and is a git repo
		if os.path.exists(self.repo_full_path + '/.git'):
			os.chdir(self.repo_full_path)
			cmd = 'git pull'
		elif os.path.exists(self.repo_full_path):
			msg = 'Error, directory "%s" already exists and is not a git repo' % self.repo_full_path
			raise CommandError(self, msg)
		else:
			cmd = 'git clone %s' % self.url

		# clone or pull
		try:
			proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		except OSError:
			raise CommandError(self, 'Unable to find "git" in $PATH')
		print('Retrieving git repo %s with "%s", this may take a while' % (self.url, cmd))
		stdout, stderr = proc.communicate()

		if proc.returncode != 0:
			print(stdout)
			raise CommandError(self, 'Unable to retrieve git repository: %s' % self.url)

		# checkout the commit
		os.chdir(self.repo_full_path)
		cmd = 'git checkout %s' % self.commitish
		proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		stdout, stderr = proc.communicate()

		if proc.returncode != 0:
			print(stdout)
			raise CommandError(self, 'Unable to checkout: %s' % self.commitish)

		# clean the directory
		cmd = 'git clean -xfd'
		proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		stdout, stderr = proc.communicate()

		if proc.returncode != 0:
			print(stdout)
			raise CommandError(self, 'Unable to clean git directory')


	def make_roll(self):
		# get roll name from version.mk
		pallet_name = ''
		if not os.path.isfile('version.mk'):
			raise CommandError(self, 'Unable to find version.mk in git repo')
		with open('version.mk') as version_file:
			for line in version_file.readlines():
				if 'ROLL' in line.split():
					pallet_name = line.split('=')[-1].strip()
					break
			else:
				raise CommandError(self, 'Could not find ROLL in version.mk')

		print('Running "make roll"...')
		cmd = 'make roll'
		proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		stdout, stderr = proc.communicate()

		if proc.returncode != 0:
			print(stdout)
			raise CommandError(self, '"make roll" had errors')
		else:
			output_file = '/tmp/%s-make-output.txt' % pallet_name
			print('saving "make" output to %s' % output_file)
			with open(output_file, 'w') as output_file:
				output_file.write(stdout)

		iso_glob  = glob.glob('{0}/build-{1}-{2}/{1}*iso'.format(
			self.repo_full_path, pallet_name, self.commitish))
		if len(iso_glob) == 1:
			print('pallet created at:\n\t%s' % iso_glob[0])


class Command(stack.commands.create.command,
		stack.commands.HostArgumentProcessor):

	"""
	Create a pallet.  You may specify either a single XML file or git URL 
	to build one pallet or a list of ISO files to build a Meta pallet.

	<arg type='string' name="pallet" repeat='1'>
	Either a list of pallet ISO files, the name of a single pallet XML
	description file, or a git URL (which ends in .git) that points to
	the source of a pallet.

	If a list of pallet ISO files is specified, they will be merged
	together into a single pallet.	Otherwise the argument is assumed to
	be the name of the XML file generated by the top level Makefile in
	the pallet's source, OR a git repo containing a valid Makefile and
	version.mk.  Private repos can be built from if the SSH key is added
	to the ssh-agent before issuing this command.
	</arg>

	<param type='string' name='name'>
	The base name for the created pallet.
	</param>
	
	<param type='string' name='version'>
	The version number of the created pallet. Default is the version of 
	stacki running on this machine.
	</param>

	<param type='string' name='release'>
	The release id of the created pallet. Default is the release id of 
	stacki running on this machine.
	</param>

	<param type='boolean' name='newest'>
	</param>

	<param type='string' name='commit-ish'>
	The git "commit-ish" object to checkout and build from a git repo.
	Can be a git branch, tag, or SHA1.  Default is 'master'.
	</param>

	<example cmd='create pallet pallet-base.xml'>
	Creates the Base pallet from the pallet-base.xml description file.
	</example>

	<example cmd='create pallet git@github.com:StackIQ/stacki-tools.git'>
	Fetches and creates the Stacki-Tools pallet from a Git repository.
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

		try:
			release = stack.release
		except AttributeError:
			release = 0

		# Yes, globals are probably bad. But this is the fastest
		# to getting what we want. Otherise have to pass all this
		# in various arg lines to the defined classes and defs 
		# in this file. Blame Greg, he said it was okay.
		global newest

		(name, version, release, newest, commit) = self.fillParams([
			('name', None),
			('version', version),
			('release', release),
			('newest', True),
			('commit-ish', 'master'),
			])

		# I'm always leaving mounts around. I'm lazy.		
		mounted = os.path.ismount('/mnt/cdrom')
		while mounted:
			os.system('umount /mnt/cdrom > /dev/null 2>&1')
			mounted = os.path.ismount('/mnt/cdrom')

		if len(args) == 0:
			raise ArgRequired(self, 'pallet')
		
		if len(args) == 1:
			base, ext = os.path.splitext(args[0])
			if ext == '.git':
				builder = GitRollBuilder(args[0], commit)
			elif ext == '.xml':
				if not os.path.isfile(args[0]):
					raise CommandError(self, 'file %s not found' % args[0])
				builder = RollBuilder(args[0], self.command, self.call)
			else:
				raise CommandError(self, 'missing xml file')
		elif len(args) > 1:
			for arg in args:
				if not os.path.isfile(arg):
					raise CommandError(self, 'file %s not found' % arg)
				base, ext = os.path.splitext(arg)
				if not ext == '.iso':
					raise CommandError(self, 'bad iso file')
			builder = MetaRollBuilder(args, name, version, release,
				self.command)
			
		builder.run()

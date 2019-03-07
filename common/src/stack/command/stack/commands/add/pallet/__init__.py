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
import subprocess
import stack.file
import stack.commands
import tempfile
from stack.download import fetch, FetchError
from stack.exception import CommandError, ParamRequired, UsageError
from urllib.parse import urlparse
from stack.util import _exec


class command(stack.commands.add.command):
	pass


class Command(command):
	"""
	Add pallet ISO images to this machine's pallet directory. This command
	copies all files in the ISOs to the local machine. The default location
	is a directory under /export/stack/pallets.

	<arg optional='1' type='string' name='pallet' repeat='1'>
	A list of pallet ISO images to add to the local machine. If no list is
	supplied, then if a pallet is mounted on /mnt/cdrom, it will be copied
	to the local machine. If the pallet is hosted on the internet, it will
	be downloaded and stored on the local machine.
	</arg>

	<param type='string' name='username'>
	If the pallet's download server requires authentication.
	</param>

	<param type='string' name='password'>
	If the pallet's download server requires authentication.
	</param>
		
	<param type='bool' name='clean'>
	If set, then remove all files from any existing pallets of the same
	name, version, and architecture before copying the contents of the
	pallets onto the local disk.  This parameter should not be set
	when adding multi-CD pallets such as the OS pallet, but should be set
	when adding single pallet CDs such as the Grid pallet.
	</param>

	<param type='string' name='dir'>
	The base directory to copy the pallet to.
	The default is: /export/stack/pallets.
	</param>

	<param type='string' name='updatedb'>
	Add the pallet info to the cluster database.
	The default is: true.
	</param>
	
	<example cmd='add pallet clean=1 kernel*iso'>
	Adds the Kernel pallet to local pallet directory.  Before the pallet is
	added the old Kernel pallet packages are removed from the pallet
	directory.
	</example>
	
	<example cmd='add pallet kernel*iso pvfs2*iso ganglia*iso'>
	Added the Kernel, PVFS, and Ganglia pallets to the local pallet
	directory.
	</example>

	<related>remove pallet</related>
	<related>enable pallet</related>
	<related>disable pallet</related>
	<related>list pallet</related>
	<related>create pallet</related>
	"""

	def copy(self, clean, prefix, updatedb, URL):
		"""Copy all the pallets from the CD to Disk"""

		# Populate the info hash. This hash contains pallet
		# information about all the pallets present on disc.

		p = subprocess.run(['find', '%s' % self.mountPoint, '-type', 'f', '-name', 'roll-*.xml'],
				   stdout=subprocess.PIPE)
		dict = {}
		for filename in p.stdout.decode().split('\n'):
			if filename:
				roll = stack.file.RollInfoFile(filename.strip())
				dict[roll.getRollName()] = roll

		if len(dict) == 0:
			
			# If the roll_info hash is empty, that means there are
			# no stacki recognizable rolls on the Disc. This mean
			# it may just be a normal OS CD like CentOS, RHEL,
			# Ubuntu, or SuSE. In any case it's a
			# foreign CD, and should be treated as such.
			#
			self.loadImplementation()
			impl_found = False
			for i in self.impl_list:
				if hasattr(self.impl_list[i], 'check_impl'):
					if self.impl_list[i].check_impl():
						impl_found = True
						res = self.runImplementation(i, (clean, prefix))
						break

			if not impl_found:
				raise CommandError(self, 'unknown pallet on %s' % self.mountPoint)

			if res:
				if updatedb:
					self.insert(res[0], res[1], res[2], res[3], res[4], URL)
				if self.dryrun:
					self.addOutput(res[0], [res[1], res[2], res[3], res[4], URL])

		#
		# Keep going even if a foreign pallet.  Safe to loop over an
		# empty list.
		#
		# For all pallets present, copy into the pallets directory.
		
		for key, info in dict.items():
			self.runImplementation('native_%s' % info.getRollOS(),
					       (clean, prefix, info))
			name	= info.getRollName()
			version	= info.getRollVersion()
			release	= info.getRollRelease()
			arch	= info.getRollArch()
			osname	= info.getRollOS()
			if updatedb:
				self.insert(name, version, release, arch, osname, URL)
			if self.dryrun:
				self.addOutput(name, [version, release, arch, osname, URL])


	def insert(self, name, version, release, arch, OS, URL):
		"""
		Insert the pallet information into the database if
		not already present.
		"""

		if self.db.count(
			'(ID) from rolls where name=%s and version=%s and rel=%s and arch=%s and os=%s',
			(name, version, release, arch, OS)
		) == 0:
			self.db.execute("""
				insert into rolls(name, version, rel, arch, os, URL)
				values (%s, %s, %s, %s, %s, %s)
				""", (name, version, release, arch, OS, URL)
			)

	# Call the sevice ludicrous-cleaner
	def clean_ludicrous_packages(self):
		_command = 'systemctl start ludicrous-cleaner'
		p = subprocess.Popen(_command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)


	def run(self, params, args):
		(clean, dir, updatedb, dryrun, username, password) = self.fillParams([
			('clean', 'n'),
			('dir', '/export/stack/pallets'),
			('updatedb', 'y'),
			('dryrun', 'n'),
			('username', None),
			('password', None),
		])

		#Validate username and password
		#need to provide either both or none
		if username and not password:
			raise UsageError(self, 'must supply a password with the username')
		if password and not username:
			raise UsageError(self, 'must supply a username with the password')

		clean = self.str2bool(clean)
		updatedb = self.str2bool(updatedb)
		self.dryrun = self.str2bool(dryrun)
		if self.dryrun:
			updatedb = False
			self.out = sys.stderr
		else:
			self.out = sys.stdout

		temp_mount_dir = tempfile.TemporaryDirectory()
		self.mountPoint = temp_mount_dir.name

		# Get a list of all the iso files mentioned in
		# the command line. Make sure we get the complete 
		# path for each file.
			
		isolist = []
		network_pallets = []
		disk_pallets    = []
		network_isolist = []
		for arg in args:
			if arg.startswith(('http', 'ftp')) and arg.endswith('.iso'):
				network_isolist.append(arg)
				continue
			elif arg.startswith(('http', 'ftp')):
				network_pallets.append(arg)
				continue
			arg = os.path.join(os.getcwd(), arg)
			if os.path.exists(arg) and arg.endswith('.iso'):
				isolist.append(arg)
			elif os.path.isdir(arg):
				disk_pallets.append(arg)
			else:
				msg = "Cannot find %s or %s is not an ISO image"
				raise CommandError(self, msg % (arg, arg))

		if self.dryrun:
			self.beginOutput()
		if not isolist and not network_pallets and not disk_pallets and not network_isolist:
			#
			# no files specified look for a cdrom
			#
			self.mountPoint = '/mnt/cdrom'
			rc = os.system('mount | grep %s' % self.mountPoint)
			if rc == 0:
				self.copy(clean, dir, updatedb, self.mountPoint)
			else:
				raise CommandError(self, 'no pallets provided and /mnt/cdrom is unmounted')

		for iso in network_isolist:
			#determine the name of the iso file and get the destined path
			filename = os.path.basename(urlparse(iso).path)
			local_path = '/'.join([os.getcwd(), filename])

			net_iso_mounted_somewhere = _exec(f'mount | grep {iso}', shell=True).stdout

			if net_iso_mounted_somewhere:
				other_mountpoint = net_iso_mounted_somewhere.split(' ')[2]
				stack.commands.Log(f'ISO with same name as {iso} already mounted on filesystem at {other_mountpoint}: Attempting to unmount.') 
				try_umount = _exec(f'umount {other_mountpoint}', shell=True)
				iso_name = os.path.basename(iso)
				if try_umount.stderr:			
					raise CommandError(self, f'Failed to unmount {iso_name} at {other_mountpoint}, pallet could not be installed.') 

			try:
				# passing True will display a % progress indicator in stdout
				local_path = fetch(iso, username, password, True)
			except FetchError as e:
				raise CommandError(self, e)

			cwd = os.getcwd()
			os.system('mount -o loop %s %s > /dev/null 2>&1' % (local_path, self.mountPoint))
			self.copy(clean, dir, updatedb, iso)
			os.chdir(cwd)
			os.system('umount %s > /dev/null 2>&1' % self.mountPoint)
			print('cleaning up temporary files ...')
			p = _exec(['rm', filename])

		if isolist:
			#
			# before we mount the ISO, make sure there are no active
			# mounts on the mountpoint
			#
			file = open('/proc/mounts')

			for line in file.readlines():
				l = line.split()
				if l[1].strip() == self.mountPoint:
					cmd = 'umount %s' % self.mountPoint
					cmd += ' > /dev/null 2>&1'
					_exec([ cmd ], shell=True)

			for iso in isolist:	# have a set of iso files
				cwd = os.getcwd()
				iso_mounted_somewhere = _exec(f'mount | grep {iso}', shell=True).stdout

				if iso_mounted_somewhere:
					other_mountpoint = iso_mounted_somewhere.split(' ')[2]
					stack.commands.Log(f'ISO with same name as {iso} already mounted on filesystem at {other_mountpoint}: Attempting to unmount.') 
					try_umount = _exec(f'umount {other_mountpoint}', shell=True)
					iso_name = os.path.basename(iso)
					if try_umount.stderr:			
						raise CommandError(self, f'Failed to unmount {iso_name} at {other_mountpoint}, pallet could not be installed.') 

				os.system('mount -o loop %s %s > /dev/null 2>&1' % (iso, self.mountPoint))
				self.copy(clean, dir, updatedb, iso)
				os.chdir(cwd)
				os.system('umount %s > /dev/null 2>&1' % self.mountPoint)
		
		if network_pallets:
			for pallet in network_pallets:
				self.runImplementation('network_pallet', (clean, dir, pallet, updatedb))
		
		if disk_pallets:
			for pallet in disk_pallets:
				self.runImplementation('disk_pallet', (clean, dir, pallet, updatedb))

		self.endOutput(header=['name', 'version', 'release', 'arch', 'os'], trimOwner=False)

		# Clear the old packages
		self.clean_ludicrous_packages()


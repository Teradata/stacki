# @copyright@
# Copyright (c) 2006 - 2018 Teradata
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
from stack.exception import CommandError
from urllib.parse import urlparse
import requests
from requests.auth import HTTPBasicAuth


class Command(stack.commands.add.command):
	"""
	Add pallet ISO images to this machine's pallet directory. This command
	copies all files in the ISOs to the local machine. The default location
	is a directory under /export/stack/pallets.

	<arg optional='1' type='string' name='pallet' repeat='1'>
	A list of pallet ISO images to add to the local machine. If no list is
	supplied, then if a pallet is mounted on /mnt/cdrom, it will be copied
	to the local machine.
	</arg>
		
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

	def copy(self, clean, prefix, updatedb, path, urlauth=None):
		#if this is a network iso and authentication is needed prep the username and password for the database
		if urlauth:
			urlauthUser = urlauth[0]
			urlauthPass = urlauth[1]
		else:
			urlauthUser = None
			urlauthPass = None
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
					self.insert(res[0], res[1], res[2], res[3], res[4], res[5], urlauthUser, urlauthPass)
				if self.dryrun:
					self.addOutput(res[0], [res[1], res[2], res[3], res[4],res[5], urlauthUser, urlauthPath])

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
			URL = path
			if updatedb:
				self.insert(name, version, release, arch, osname, URL, urlauthUser, urlauthPass)
			if self.dryrun:
				self.addOutput(name, [version, release, arch, osname, URL, urlauthUser, urlauthPass])


	def insert(self, name, version, release, arch, OS, URL, urlauthUser, urlauthPass):
		"""
		Insert the pallet information into the database if
		not already present.
		"""
		rows = self.db.execute("""
			select * from rolls where
			name='%s' and version='%s' and rel='%s' and arch='%s' and os='%s'
			""" % (name, version, release, arch, OS))
		if not rows:
			self.db.execute("""insert into rolls
				(name, version, rel, arch, os, URL, urlauthUser, urlauthPass) values
				('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')
				""" % (name, version, release, arch, OS, URL, urlauthUser, urlauthPass))

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
		clean = self.str2bool(clean)
		updatedb = self.str2bool(updatedb)
		self.dryrun = self.str2bool(dryrun)
		if self.dryrun:
			updatedb = False
			self.out = sys.stderr
		else:
			self.out = sys.stdout

		self.mountPoint = '/mnt/cdrom'
		if not os.path.exists(self.mountPoint):
			os.makedirs(self.mountPoint)

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
			if arg.startswith(('http', 'ftp')):
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
			rc = os.system('mount | grep %s' % self.mountPoint)
			if rc == 0:
				self.copy(clean, dir, updatedb, self.mountpoint)
			else:
				raise CommandError(self, 'no pallets provided and /mnt/cdrom is unmounted')

		if network_isolist:
			for iso in network_isolist:
				#determine the name of the iso file and get the destined path
				filename = os.path.basename(urlparse(iso).path)
				local_path = '/'.join([os.getcwd(),filename])

				print(f'beginning download of {iso}\nthis may take awhile...')
				try:
					if username and password:
						urlauth = [username, password]

						#results = subprocess.run(['wget', '--user', username, '--password', password, iso])

						s = requests.Session()
						s.auth = HTTPBasicAuth(username, password)
						r = s.get(iso, stream=True)
					else:
						urlauth=None
						r = requests.get(iso, stream=True)

				except Exception as e:
					print(f'error downloading iso: {e}')
					continue

				content_length = int(r.headers.get('content-length')) / 1000000


				#verify that there are no http errors
				if r.status_code == 401:
					print ('error 401 invalid credentials or invalid url. aborting.')
					continue
				if r.status_code == 404:
					print ('error 404 this is a dead url. aborting')
					continue
				elif not r.ok:
					print ('error downloading file. requests not "ok". aborting.')


				progress = 0
				chunk_size = 1000000
				#determine how many digits long the size of the iso is so we can display a clean progress indicator
				content_digits = len(str(content_length))
				with open(local_path, 'wb') as f:
					for chunk in (item for item in r.iter_content(chunk_size=chunk_size) if item):
						f.write(chunk)
						f.flush()
						progress += 1
						print(f'MB remaining: {int(content_length-progress):{content_digits}}', end='\r')
					#watch out for premature connection closures by the download server
					#if the entire file has not been downloaded, don't pass an incomplete iso
					if progress < content_length:
						print(f'error downloading {iso}\ndownload unable to complete. the connection may have been prematurely closed by the server.')
						print(f'failed at {progress} MB out of {int(content_length)} MB')
						print('cleaning up ...')
						p = subprocess.run(['rm', filename])
						continue

				cwd = os.getcwd()
				os.system('mount -o loop %s %s > /dev/null 2>&1' % (local_path, self.mountPoint))
				self.copy(clean, dir, updatedb, iso, urlauth)
				os.chdir(cwd)
				os.system('umount %s > /dev/null 2>&1' % self.mountPoint)
				print('cleaning up temporary files ...')
				p = subprocess.run(['rm', filename])

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
					subprocess.run([ cmd ], shell=True)

			for iso in isolist:	# have a set of iso files
				cwd = os.getcwd()
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

RollName = "stacki"

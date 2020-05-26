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

import pathlib
import shutil
import tempfile
from textwrap import dedent
import os
from operator import attrgetter

import stack.commands
from stack.argument_processors.pallet import (
	PalletArgProcessor,
	PALLET_HOOK_DIRNAME,
)
from stack import probepal
from stack.util import flatten
from stack.exception import CommandError, UsageError

# Set up our info_getter because we expect a certain order of attribute values,
# I.E. some code is doing tuple unpacking.
probepal_info_getter = attrgetter(
	"name",
	"version",
	"release",
	"distro_family",
	"arch",
)


class command(stack.commands.add.command):
	pass


class Command(PalletArgProcessor, command):
	"""
	Add pallets to this machine's pallet directory. This command copies all
	files in ISOs or paths recognized by stacki to be pallets to the local
	machine. The default location is a directory under /export/stack/pallets.
	See also the 'probepal' utility to ascertain how, if at all, stacki will
	recognize it.

	<arg optional='1' type='string' name='pallet' repeat='1'>
	A list of pallets to add to the local machine. If no list is supplied
	stacki will check if a pallet is mounted on /mnt/cdrom, and if so copy it
	to the local machine. If the pallet is hosted on the internet, it will
	be downloaded to a temporary directory before being added.  All temporary
	files and mounts will be cleaned up, with the exception of /mnt/cdrom.
	</arg>

	<param type='string' name='username'>
	A username that will be used for authenticating to any remote pallet locations
	</param>

	<param type='string' name='password'>
	A password that will be used for authenticating to any remote pallet locations
	</param>

	<param type='bool' name='clean'>
	If set, then remove all files from any existing pallets of the same
	name, version, and architecture before copying the contents of the
	pallets onto the local disk.
	</param>

	<param type='string' name='dir'>
	The base directory to copy the pallet to.
	The default is: /export/stack/pallets.
	</param>

	<param type='string' name='updatedb'>
	Add the pallet info to the cluster database.
	The default is: true.
	</param>

	<param type='bool' name='run_hooks'>
	Controls whether pallets hooks are run. This defaults to True.
	</param>

	<param type='string' name='checksum'>
	Check the pallet against the given checksum.

	If you want to avoid collisions, be sure to use sha256 and/or sha512 (at least until a point when collisions
	are detected with these algorithms)

	Supported checksums at the moment are: md5, sha1, sha256, sha512.
	e.g. checksum="sha256:$SHA256"

	For multiple pallets given, separate the checksum by commas.
	</param>

	<example cmd='add pallet clean=true kernel*iso'>
	Adds the Kernel pallet to local pallet directory.  Before the pallet is
	added the old Kernel pallet packages are removed from the pallet
	directory.
	</example>

	<example cmd='add pallet kernel*iso https://10.0.1.3/pallets/'>
	Added the Kernel pallet along with any pallets found at the remote server
	 to the local pallet directory.
	</example>

	<example cmd='add pallet my-os.iso checksum="sha256:$SHA256"'>
	Check the SHA256 checksum of my-os.iso against the value of $SHA256.
	</example>

	<example cmd='add pallet os-1.iso os-2.iso checksum="sha256:$SHA256_ISO_1,sha256:$SHA256_ISO_2"'>
	Check multiple pallets. First check os-1.iso checksum against the value of $SHA256_ISO_1 followed by the os-2.iso
	checksum against the value of $SHA256_ISO_2.
	</example>

	<related>remove pallet</related>
	<related>enable pallet</related>
	<related>disable pallet</related>
	<related>list pallet</related>
	<related>create pallet</related>
	<related>create new pallet</related>
	"""

	def write_pallet_xml(self, stacki_pallet_root, pallet_info):
		'''
		Create a roll-*.xml file compatible with the rest of stacki's tooling
		note: if we copied an existing roll-*.xml, don't overwrite it here as it may have
		more metadata
		'''
		destdir = pathlib.Path(stacki_pallet_root).joinpath(*probepal_info_getter(pallet_info))
		name, version, release, distro_family, arch = probepal_info_getter(pallet_info)

		if destdir.joinpath(f'roll-{name}.xml').exists():
			return

		with open(f'{destdir}/roll-{name}.xml', 'w') as xml:
			xml.write(dedent(f'''\
			<roll name="{name}" interface="6.0.2">
			<info version="{version}" release="{release}" arch="{arch}" os="{distro_family}"/>
			<iso maxsize="0" addcomps="0" bootable="0"/>
			<rpm rolls="0" bin="1" src="0"/>
			</roll>
			'''))


	def copy(self, stacki_pallet_root, pallet_info, clean):
		'''
		Copy a pallet to the local filesystem

		Specifically, rsync from `pallet_info.pallet_root` to
		`stacki_pallet_root`/name/version/release/os/arch/
		'''
		pallet_dir = pallet_info.pallet_root
		destdir = pathlib.Path(stacki_pallet_root).joinpath(*probepal_info_getter(pallet_info))

		if destdir.exists() and clean:
			self.notify(f'Cleaning {"-".join(probepal_info_getter(pallet_info))} from pallets directory')
			shutil.rmtree(destdir)

		self.notify(f'Copying {"-".join(probepal_info_getter(pallet_info))} ...')

		destdir.mkdir(parents=True, exist_ok=True)

		# use rsync to perform the copy
		# archive implies
		# --recursive,
		# --links - copy symlinks as symlinks
		# --perms - preserve permissions
		# --times - preserve mtimes
		# --group - preserve group
		# --owner - preserve owner
		# --devices - preserve device files
		# --specials - preserve special files
		# we then overwrite the permissions to make apache happy.
		cmd = f'rsync --archive --chmod=D755 --chmod=F644 --exclude "TRANS.TBL" {pallet_dir}/ {destdir}/'
		result = self._exec(cmd, shlexsplit=True)
		if result.returncode != 0:
			raise CommandError(self, f'Unable to copy pallet:\n{result.stderr}')

		# Copy any pallet hooks into the correct location
		script_dir = pathlib.Path(pallet_dir) / PALLET_HOOK_DIRNAME
		if script_dir.is_dir():
			# Create the pallet hook directory if it doesn't already exist.
			dest_hook_dir = self.get_pallet_hook_directory(pallet_info=pallet_info)
			dest_hook_dir.mkdir(parents=True, exist_ok=True)
			# Copy the hooks to the appropriate destination.
			# ensure with chmod that hooks are executable by at least root
			cmd = f'rsync --archive --chmod=F744 --exclude "TRANS.TBL" {script_dir}/ {dest_hook_dir}/'
			result = self._exec(cmd, shlexsplit=True)
			if result.returncode != 0:
				raise CommandError(self, f'Unable to copy pallet hooks:\n{result.stderr}')

		return destdir


	def update_db(self, pallet_info, URL):
		"""
		Insert the pallet information into the database if not already present.
		"""

		rows = self.db.select(
			'id FROM rolls WHERE name=%s AND version=%s AND rel=%s AND os=%s AND arch=%s',
			probepal_info_getter(pallet_info)
		)

		if len(rows) == 0:
			# New pallet
			self.db.execute("""
				insert into rolls(name, version, rel, os, arch, URL)
				values (%s, %s, %s, %s, %s, %s)
				""", (*probepal_info_getter(pallet_info), URL)
			)
		else:
			# Re-added the pallet. Update the URL.
			self.db.execute('UPDATE rolls SET url=%s WHERE id=%s', (URL, rows[0][0]))

	def perform_checksum(self, pallet_arg, iso_name):
		if pallet_arg in self.checksum:
			checksum_type, checksum_value = self.checksum[pallet_arg]
			self.notify(f'Checking {iso_name} matches {checksum_type}={checksum_value}...')
			proc = self._exec(
				cmd = f'{checksum_type}sum -c',
				shlexsplit=True,
				input=f'{checksum_value} {iso_name}\n'
			)
			if proc.returncode != 0:
				raise CommandError(
					self,
					f'Checksum for {iso_name} does not match given checksum ({checksum_type}:{checksum_value}).\n'
					f'{proc.stdout}\n{proc.stderr}'
				)

	def mount(self, iso_name, mount_point):
		'''
		mount `iso_name` to `mount_point`
		we automatically register an unmount callback
		'''

		# mount readonly explicitly to get around a weird behavior
		# in sles12 that prevents re-mounting an already mounted iso

		proc = self._exec(f'mount --read-only -o loop {iso_name} {mount_point}', shlexsplit=True)
		if proc.returncode != 0:
			msg = f'Pallet could not be added - unable to mount {iso_name}.'
			msg += f'\nTried: {" ".join(str(arg) for arg in proc.args)}'
			raise CommandError(self, f'{msg}\n{proc.stdout}\n{proc.stderr}')
		self.deferred.callback(self.umount, iso_name, mount_point)


	def umount(self, iso_name, mount_point):
		'''
		un-mount `mount_point`, first checking to see if it is actually mounted
		'''

		proc = self._exec(f'mount | grep {mount_point}', shell=True)
		if proc.returncode == 1 and proc.stdout.strip() == '':
			return
		proc = self._exec(f'umount {mount_point}', shlexsplit=True)
		if proc.returncode != 0:
			msg = f'Pallet could not be unmounted from {mount_point} ({iso_name}).'
			msg += f'\nTried: {" ".join(str(arg) for arg in proc.args)}'
			raise CommandError(self, f'{msg}\n{proc.stdout}\n{proc.stderr}')


	def run(self, params, args):
		clean, stacki_pallet_dir, updatedb, run_hooks, checksum, self.username, self.password = self.fillParams([
			('clean', False),
			('dir', '/export/stack/pallets'),
			('updatedb', True),
			('run_hooks', True),
			('checksum', None),
			('username', None),
			('password', None),
		])

		# need to provide either both or none
		if (self.username or self.password) and not all((self.username, self.password)):
			raise UsageError(self, 'must supply a password along with the username')

		clean = self.str2bool(clean)
		updatedb = self.str2bool(updatedb)
		run_hooks = self.str2bool(run_hooks)

		self.checksum = {}
		if checksum:
			valid_checksums = ['md5', 'sha1', 'sha256', 'sha512']
			bad_paths = []
			for pallets in args:
				if os.path.isdir(pallets):
					bad_paths.append(pallets)

			if bad_paths:
				raise UsageError(
					self,
					f"One or more paths was specified with a checksum that is a directory. Invalid paths are: "
					f"{', '.join(bad_paths)}"
				)

			if len(checksum.split(',')) != len(args):
				raise UsageError(self, "Checksum is required for each pallet.")

			invalid_checksums = []
			for i, pallet in enumerate(args):
				try:
					checksum_type, checksum_value = checksum.split(',')[i].split(':')
				except ValueError:
					raise UsageError(self, 'You must supply a checksum in the format of <type>:<value>')
				if checksum_type not in valid_checksums:
					invalid_checksums.append(checksum_type)
				else:
					if pallet.startswith(('https://', 'http://', 'ftp://')):
						path = pallet
					else:
						path = str(pathlib.Path(pallet).resolve())
					self.checksum[path] = (checksum_type, checksum_value)

			if len(invalid_checksums) > 0:
				raise UsageError(
					self,
					f"Invalid checksum type(s) given: {', '.join(invalid_checksums)}. "
					f"Valid checksums are: [{', '.join(valid_checksums)}."
				)

		# special case: no args were specified - check if a pallet is mounted at /mnt/cdrom
		if not args:
			mount_point = '/mnt/cdrom'
			result = self._exec(f'mount | grep {mount_point}', shell=True)
			if result.returncode != 0:
				raise CommandError(self, 'no pallets specified and /mnt/cdrom is unmounted')
			args.append(mount_point)

		# resolve args and check for existence
		bad_args = []
		for i, arg in enumerate(list(args)):
			# TODO: is this a problem?
			if arg.startswith(('https://', 'http://', 'ftp://')):
				args[i] = arg
				continue

			p = pathlib.Path(arg)
			if not p.exists():
				bad_args.append(arg)
			else:
				args[i] = str(p.resolve())

		if bad_args:
			msg = 'The following arguments appear to be local paths that do not exist: '
			raise CommandError(self, msg + ', '.join(bad_args))

		# most plugins will need a temporary directory, so allocate them here so we do cleanup
		# 'canonical_arg' is the arg provided by the user, but cleaned to be explicit (relative
		# paths resolved, etc)
		# 'exploded_path' is the directory where we will start searching for pallets
		# 'matched_pallets' is a list of pallet_info objects found at that path.
		pallet_args = {}
		for arg in args:
			tmpdir = tempfile.mkdtemp()
			self.deferred.callback(shutil.rmtree, tmpdir)
			pallet_args[arg] = {
				'canonical_arg': arg,
				'exploded_path': tmpdir,
				'matched_pallets': [],
			}

		self.runPlugins(pallet_args)

		prober = probepal.Prober()
		pallet_infos = prober.find_pallets(
			*[pallet_args[path]['exploded_path'] for path in pallet_args]
		)

		# pallet_infos returns a dict {path: [pallet1, ...]}
		# note the list - an exploded_path can point to a jumbo pallet

		for path, pals in pallet_infos.items():
			for arg in pallet_args:
				if pallet_args[arg]['exploded_path'] == path:
					pallet_args[arg]['matched_pallets'] = pals

		# TODO what to do if we match something twice.
		bad_args = [arg for arg, info in pallet_args.items() if not info['matched_pallets']]
		if bad_args:
			msg = 'The following arguments do not appear to be pallets: '
			raise CommandError(self, msg + ', '.join(bad_args))

		# work off of a copy of pallet args, as we modify it as we go
		for arg, data in pallet_args.copy().items():
			if len(data['matched_pallets']) == 1:
				pallet_args[arg]['exploded_path'] = data['matched_pallets'][0].pallet_root
				continue

			# delete the arg pointing to a jumbo and replace it with N new 'dummy' args
			del pallet_args[arg]
			for pal in data['matched_pallets']:
				fake_arg_name = '-'.join(probepal_info_getter(pal))
				pallet_args[fake_arg_name] = data.copy()
				pallet_args[fake_arg_name]['exploded_path'] = pal.pallet_root
				pallet_args[fake_arg_name]['matched_pallets'] = [pal]

		# we want to be able to go tempdir to arg
		# this is because we want `canonical_arg` to be what goes in as the `URL` field in the db
		paths_to_args = {data['exploded_path']: data['canonical_arg'] for data in pallet_args.values()}

		# we have everything we need, copy the pallet to the fs, add it to the db, and maybe patch it
		self.beginOutput()
		for pallet in flatten(pallet_infos.values()):
			self.copy(stacki_pallet_dir, pallet, clean)
			self.write_pallet_xml(stacki_pallet_dir, pallet)
			if updatedb:
				self.update_db(pallet, paths_to_args[pallet.pallet_root])

			# Run pallet hooks for the add operation.
			if run_hooks:
				self.run_pallet_hooks(operation="add", pallet_info=pallet)
			self.addOutput(pallet.name, (pallet.version, pallet.release, pallet.arch, pallet.distro_family))
		self.endOutput(header=['pallet', 'version', 'release', 'arch', 'os'])

		# Clear the old packages
		self._exec('systemctl start ludicrous-cleaner'.split())

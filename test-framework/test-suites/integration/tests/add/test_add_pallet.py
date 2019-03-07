import json
import os
from contextlib import ExitStack
from textwrap import dedent

class TestAddPallet:
	def test_no_pallet(self, host):
		# Call add pallet with nothign mounted and no pallets passed in
		result = host.run('stack add pallet')
		assert result.rc == 255
		assert result.stderr == 'error - no pallets provided and /mnt/cdrom is unmounted\n'

	def test_invalid(self, host):
		# Add something that doesn't exist
		result = host.run('stack add pallet /export/test.iso')
		assert result.rc == 255
		assert result.stderr == 'error - Cannot find /export/test.iso or /export/test.iso is not an ISO image\n'

	def test_username_no_password(self, host, create_pallet_isos):
		result = host.run(f'stack add pallet {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso username=test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - must supply a password with the username
			[pallet ...] [clean=bool] [dir=string] [password=string] [updatedb=string] [username=string]
		''')

	def test_password_no_username(self, host, create_pallet_isos):
		result = host.run(f'stack add pallet {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso password=test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - must supply a username with the password
			[pallet ...] [clean=bool] [dir=string] [password=string] [updatedb=string] [username=string]
		''')

	def test_minimal(self, host, create_pallet_isos, revert_export_stack_pallets):
		# Add our minimal pallet
		result = host.run(f'stack add pallet {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso')
		assert result.rc == 0
		assert result.stdout == 'Copying minimal 1.0-sles12 to pallets ...\n'

		# Check it made it in as expected
		result = host.run('stack list pallet minimal output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'name': 'minimal',
				'version': '1.0',
				'release': 'sles12',
				'arch': 'x86_64',
				'os': 'sles',
				'boxes': ''
			}
		]

	def test_no_mountpoint(self, host, rmtree, create_pallet_isos, revert_export_stack_pallets):
		# Remove our mountpoint
		rmtree('/mnt/cdrom')

		# Add our minimal pallet
		result = host.run(f'stack add pallet {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso')
		assert result.rc == 0
		assert result.stdout == 'Copying minimal 1.0-sles12 to pallets ...\n'

		# Check it made it in as expected
		result = host.run('stack list pallet minimal output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'name': 'minimal',
				'version': '1.0',
				'release': 'sles12',
				'arch': 'x86_64',
				'os': 'sles',
				'boxes': ''
			}
		]

	def test_mountpoint_in_use(self, host, create_pallet_isos, revert_export_stack_pallets):
		# Mount an ISO to simulate something left mounted
		result = host.run(f'mount {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso /mnt/cdrom')
		assert result.rc == 0
		
		# Add our minimal pallet
		# On SLES since add pallet is using a temporary directory to mount pallets, it complains about
		# an iso with the same name being mounted twice, so add pallet attempts to unmount the iso elsewhere  
		# but if it can't, an error is thrown
		result = host.run(f'stack add pallet {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso')
		assert result.rc == 0
		assert result.stdout == 'Copying minimal 1.0-sles12 to pallets ...\n'

		# Check it made it in as expected
		result = host.run('stack list pallet minimal output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'name': 'minimal',
				'version': '1.0',
				'release': 'sles12',
				'arch': 'x86_64',
				'os': 'sles',
				'boxes': ''
			}
		]

	def test_mountpoint_in_use_mnt(self, host, create_blank_iso, create_pallet_isos, revert_export_stack_pallets):
		with ExitStack() as cleanup:
			# Mount an ISO to simulate another iso left mounted in /mnt
			result = host.run(f'mount {create_blank_iso}/blank.iso /mnt')
			assert result.rc == 0

			#Unmount the iso no matter what happens after test exits
			cleanup.callback(host.run, 'umount /mnt')

			# Add our minimal pallet
			result = host.run(f'stack add pallet {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso')
			assert result.rc == 0
			assert result.stdout == 'Copying minimal 1.0-sles12 to pallets ...\n'

			# Check it made it in as expected
			result = host.run('stack list pallet minimal output-format=json')
			assert result.rc == 0
			assert json.loads(result.stdout) == [
				{
					'name': 'minimal',
					'version': '1.0',
					'release': 'sles12',
					'arch': 'x86_64',
					'os': 'sles',
					'boxes': ''
				}
			]
		
			# Unmount ISO  
			result = host.run(f'umount /mnt')
			assert result.rc == 0

	def test_mounted_cdrom(self, host, create_pallet_isos, revert_export_stack_pallets):
		# Mount our pallet
		result = host.run(f'mount {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso /mnt/cdrom')
		assert result.rc == 0

		# Add our minimal pallet that is already mounted
		result = host.run('stack add pallet')
		assert result.rc == 0
		assert result.stdout == dedent(f'''\
			{create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso on /mnt/cdrom type iso9660 (ro,relatime)
			Copying minimal 1.0-sles12 to pallets ...
		''')

		# Check it made it in as expected
		result = host.run('stack list pallet minimal output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'name': 'minimal',
				'version': '1.0',
				'release': 'sles12',
				'arch': 'x86_64',
				'os': 'sles',
				'boxes': ''
			}
		]

	def test_minimal_dryrun(self, host, create_pallet_isos):
		# Add our minimal pallet as a dryrun
		result = host.run(f'stack add pallet {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso dryrun=true')
		assert result.rc == 0
		assert result.stdout == dedent(f'''\
			NAME    VERSION RELEASE ARCH   OS
			minimal 1.0     sles12  x86_64 sles {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso
		''')

		# Confirm it didn't get added to the DB
		result = host.run('stack list pallet minimal')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "minimal" argument is not a valid pallet
			[pallet ...] {expanded=bool} [arch=string] [os=string] [release=string] [version=string]
		''')

	def test_duplicate(self, host, create_pallet_isos, revert_export_stack_pallets):
		# Add our minimal pallet
		result = host.run(f'stack add pallet {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso')
		assert result.rc == 0
		assert result.stdout == 'Copying minimal 1.0-sles12 to pallets ...\n'

		# Add our minimal pallet again
		result = host.run(f'stack add pallet {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso')
		assert result.rc == 0
		assert result.stdout == 'Copying minimal 1.0-sles12 to pallets ...\n'

		# Adding the same pallet multiple times should only result in a
		# single pallet in the database
		result = host.run('stack list pallet minimal output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'name': 'minimal',
				'version': '1.0',
				'release': 'sles12',
				'arch': 'x86_64',
				'os': 'sles',
				'boxes': ''
			}
		]

	def test_pallet_already_mounted(self,host,create_pallet_isos):
		with ExitStack() as cleanup: 
			# Mount our pallet
			result = host.run(f'mount {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso /mnt/cdrom')
			assert result.rc == 0
			
			# Can't unmount duplicate pallet
			current_dir = host.run('pwd').stdout.strip()
			os.chdir('/mnt/cdrom/')

			# Ensure we are in the directory we started the test in
			# and iso is unmounted
			cleanup.callback(os.chdir, current_dir)
			cleanup.callback(host.run, 'umount /mnt/cdrom')

			# SLES doesn't like isos with the same name mounted in two different places
			# Add pallet handles this by unmounting duplicate named mounted isos, but should 
			# also handle when that isn't possible
			result = host.run(f'stack add pallet {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso')
			assert result.rc == 255
			assert 'error - Failed to unmount minimal-1.0-sles12.x86_64.disk1.iso at /mnt/cdrom' in result.stderr

			# Change back to the directory we came from
			os.chdir(current_dir)

			# Unmount ISO  
			result = host.run(f'umount /mnt/cdrom')
			assert result.rc == 0

	def test_add_OS_pallet_again(self, host, host_os, revert_export_stack_pallets):
		# Add our OS pallet, which is already added so it should be quick
		if host_os == 'sles':
			result = host.run('stack add pallet /export/isos/SLE-12-SP3-Server-DVD-x86_64-GM-DVD1.iso')
			assert result.rc == 0
			assert result.stdout == 'Copying "SLES" (12,x86_64) pallet ...\nPatching SLES pallet\n'
		else:
			result = host.run('stack add pallet /export/isos/CentOS-7-x86_64-Everything-1708.iso')
			assert result.rc == 0
			assert result.stdout == 'Copying CentOS 7-redhat7 pallet ...\n'

	def test_add_OS_pallet_dryrun(self, host, host_os):
		# Add our OS pallet as a dryrun
		if host_os == 'sles':
			result = host.run('stack add pallet /export/isos/SLE-12-SP3-Server-DVD-x86_64-GM-DVD1.iso dryrun=true')
			assert result.rc == 0
			assert result.stdout == dedent('''\
				NAME VERSION RELEASE ARCH   OS
				SLES 12      sp3     x86_64 sles /export/isos/SLE-12-SP3-Server-DVD-x86_64-GM-DVD1.iso
			''')
		else:
			result = host.run('stack add pallet /export/isos/CentOS-7-x86_64-Everything-1708.iso dryrun=true')
			assert result.rc == 0
			assert result.stdout == dedent('''\
				NAME   VERSION RELEASE ARCH   OS
				CentOS 7       redhat7 x86_64 redhat /export/isos/CentOS-7-x86_64-Everything-1708.iso
			''')

	def test_disk_pallet(self, host, test_file):
		# Add the minimal pallet from the disk
		result = host.run(f'stack add pallet {test_file("pallets/minimal")}')
		assert result.rc == 0

		# Check it made it in as expected
		result = host.run('stack list pallet minimal output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'name': 'minimal',
				'version': '1.0',
				'release': 'sles12',
				'arch': 'x86_64',
				'os': 'sles',
				'boxes': ''
			}
		]

	def test_network_iso(self, host, run_pallet_isos_server, revert_export_stack_pallets):
		# Add the minimal pallet ISO from the network
		result = host.run('stack add pallet http://127.0.0.1:8000/minimal-1.0-sles12.x86_64.disk1.iso')
		assert result.rc == 0

		# Check it made it in as expected
		result = host.run('stack list pallet minimal output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'name': 'minimal',
				'version': '1.0',
				'release': 'sles12',
				'arch': 'x86_64',
				'os': 'sles',
				'boxes': ''
			}
		]

	def test_network_directory(self, host, run_file_server, revert_export_stack_pallets):
		# Add the minimal pallet directory from the network
		result = host.run('stack add pallet http://127.0.0.1:8000/pallets/minimal/1.0/sles12/sles/x86_64')
		assert result.rc == 0

		# Check it made it in as expected
		result = host.run('stack list pallet minimal output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'name': 'minimal',
				'version': '1.0',
				'release': 'sles12',
				'arch': 'x86_64',
				'os': 'sles',
				'boxes': ''
			}
		]

	def test_failed_download(self, host, run_file_server):
		result = host.run('stack add pallet http://127.0.0.1:8000/test.iso')
		assert result.rc == 255
		assert result.stderr == 'error - unable to download test.iso: http error 404\n'

	def test_invalid_iso(self, host, create_blank_iso):
		with ExitStack() as cleanup:
			result = host.run(f'stack add pallet {create_blank_iso}/blank.iso')
			leftover_iso = host.run('mount | grep /tmp/tmp').stdout.split(' ')[2]

			#Make ISO unmounted, not just deleted
			cleanup.callback(host.run, f'umount {leftover_iso}')
			assert result.rc == 255
			assert 'error - unknown pallet on /tmp' in result.stderr  

import json
from operator import itemgetter
from contextlib import ExitStack
from textwrap import dedent

class TestAddPallet:
	def test_no_pallet(self, host):
		# Call add pallet with nothing mounted and no pallets passed in
		result = host.run('stack add pallet')
		assert result.rc == 255
		assert result.stderr == 'error - no pallets specified and /mnt/cdrom is unmounted\n'

	def test_invalid(self, host):
		# Add something that doesn't exist
		result = host.run('stack add pallet /export/test.iso')
		assert result.rc == 255
		assert result.stderr == 'error - The following arguments appear to be local paths that do not exist: /export/test.iso\n'

	def test_username_no_password(self, host, create_pallet_isos):
		result = host.run(f'stack add pallet {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso username=test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - must supply a password along with the username
			[pallet ...] [clean=bool] [dir=string] [password=string] [run_hooks=bool] [updatedb=string] [username=string]
		''')

	def test_password_no_username(self, host, create_pallet_isos):
		result = host.run(f'stack add pallet {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso password=test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - must supply a password along with the username
			[pallet ...] [clean=bool] [dir=string] [password=string] [run_hooks=bool] [updatedb=string] [username=string]
		''')

	def test_minimal(self, host, create_pallet_isos, revert_export_stack_pallets):
		# Add our minimal pallet
		result = host.run(f'stack add pallet {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso')
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

	def test_multiple_isos(self, host, host_os, create_pallet_isos, revert_export_stack_pallets):
		# Add our minimal pallet
		minimal = f'{create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso'
		other_iso = f'{create_pallet_isos}/test-different-arch-1.0-prod.arm.disk1.iso'

		result = host.run(f'stack add pallet {minimal} {other_iso}')
		assert result.rc == 0

		# Check it made it in as expected
		result = host.run('stack list pallet minimal test-different-arch output-format=json')
		assert result.rc == 0
		assert sorted(json.loads(result.stdout), key=itemgetter('name')) == [
			{
				'name': 'minimal',
				'version': '1.0',
				'release': 'sles12',
				'arch': 'x86_64',
				'os': 'sles',
				'boxes': ''
			},
			{
				'arch': 'arm',
				'boxes': '',
				'name': 'test-different-arch',
				'os': 'sles',
				'release': 'prod',
				'version': '1.0'
			}
		]

	def test_no_mountpoint(self, host, rmtree, create_pallet_isos, revert_export_stack_pallets):
		# Remove our mountpoint
		rmtree('/mnt/cdrom')

		# Add our minimal pallet
		result = host.run(f'stack add pallet {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso')
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

	def test_mountpoint_in_use(self, host, create_pallet_isos, revert_export_stack_pallets):
		''' current code should not care about double mounted iso's, or anything mounted in /mnt/cdrom '''
		# Mount an ISO to simulate something left mounted
		with ExitStack() as cleanup:
			result = host.run(f'mount {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso /mnt/cdrom')
			assert result.rc == 0
			#Unmount the iso no matter what happens after test exits
			cleanup.callback(host.run, 'umount /mnt/cdrom')

			result = host.run(f'stack add pallet {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso')
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

	def test_mounted_cdrom(self, host, create_pallet_isos, revert_export_stack_pallets):
		with ExitStack() as cleanup:
			# Mount our pallet
			result = host.run(f'mount | grep /mnt/cdrom')
			print(result)
			result = host.run(f'mount --read-only {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso /mnt/cdrom')
			assert result.rc == 0

			cleanup.callback(host.run, 'umount /mnt/cdrom')

			# Add our minimal pallet that is already mounted
			result = host.run('stack add pallet')
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

	def test_duplicate(self, host, create_pallet_isos, revert_export_stack_pallets):
		# Add our minimal pallet
		result = host.run(f'stack add pallet {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso')
		assert result.rc == 0

		# Add our minimal pallet again
		result = host.run(f'stack add pallet {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso')
		assert result.rc == 0

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

	def test_pallet_already_mounted(self, host, create_pallet_isos, revert_export_stack_pallets):
		''' shouldn't matter if an iso is mounted elsewhere, we should still be able to add it as a pallet '''
		with ExitStack() as cleanup:
			# Mount our pallet
			result = host.run(f'mount | grep /mnt/cdrom')
			print(result)
			result = host.run(f'mount --read-only {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso /mnt/cdrom')
			assert result.rc == 0

			cleanup.callback(host.run, 'umount /mnt/cdrom')

			# Unmount ISO
			result = host.run(f'umount /mnt/cdrom')
			assert result.rc == 0

			# Add our minimal pallet that is already mounted
			result = host.run(f'stack add pallet {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso')
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

	def test_disk_pallet(self, host, test_file, revert_export_stack_pallets):
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

	def test_network_directory_with_extra_slash(self, host, run_file_server, revert_export_stack_pallets):
		''' add pallet should clean up the extra slash - this was a bug we found in stackios :( '''
		# Add the minimal pallet directory from the network
		result = host.run('stack add pallet http://127.0.0.1:8000/pallets//minimal/1.0/sles12/sles/x86_64')
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
		result = host.run(f'stack add pallet {create_blank_iso}/blank.iso')

		#Make ISO unmounted, not just deleted
		assert result.rc == 255
		assert result.stderr.startswith(f'error - The following arguments do not appear to be pallets: {create_blank_iso}/blank.iso')

	def test_jumbo_pallet(self, host, test_file, revert_export_stack_pallets):
		print(f'stack add pallet {test_file("pallets/jumbo/")}')
		result = host.run(f'stack add pallet {test_file("pallets/jumbo/")}')
		assert result.rc == 0

		# Check it made it in as expected
		result = host.run('stack list pallet minimal maximal output-format=json')
		assert result.rc == 0

		assert sorted(json.loads(result.stdout), key=itemgetter('name')) == [
			{
				'name': 'maximal',
				'version': '1.0',
				'release': 'sles12',
				'arch': 'x86_64',
				'os': 'sles',
				'boxes': ''
			},
			{
				'name': 'minimal',
				'version': '1.0',
				'release': 'sles12',
				'arch': 'x86_64',
				'os': 'sles',
				'boxes': ''
			},
		]

	def test_add_pallet_updates_url(self, host, run_pallet_isos_server, create_pallet_isos, revert_export_stack_pallets):
		# Add our minimal pallet
		result = host.run(f'stack add pallet {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso')
		assert result.rc == 0

		result = host.run('stack list pallet minimal expanded=true output-format=json')
		assert result.rc == 0

		# Make sure we have the expected local path
		result_json = json.loads(result.stdout)
		assert result_json[0]['url'].startswith("/tmp/")
		del result_json[0]['url']

		assert  result_json == [
			{
				'name': 'minimal',
				'version': '1.0',
				'release': 'sles12',
				'arch': 'x86_64',
				'os': 'sles',
				'boxes': ''
			}
		]

		# Now add it from with a URL, and see that the url field is updated
		result = host.run('stack add pallet http://127.0.0.1:8000/minimal-1.0-sles12.x86_64.disk1.iso')
		assert result.rc == 0

		# Check it made it in as expected, and the url is updated
		result = host.run('stack list pallet minimal expanded=true output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'name': 'minimal',
				'version': '1.0',
				'release': 'sles12',
				'arch': 'x86_64',
				'os': 'sles',
				'boxes': '',
				'url': 'http://127.0.0.1:8000/minimal-1.0-sles12.x86_64.disk1.iso'
			}
		]

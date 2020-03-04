import json
import shutil
from textwrap import dedent


class TestRemovePallet:
	def test_no_pallet(self, host):
		result = host.run('stack remove pallet')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "pallet" argument is required
			{pallet ...} [arch=string] [os=string] [release=string] [run_hooks=bool] [version=string]
		''')

	def test_invalid(self, host):
		result = host.run('stack remove pallet test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid pallet
			{pallet ...} [arch=string] [os=string] [release=string] [run_hooks=bool] [version=string]
		''')

	def test_no_parameters(self, host, create_pallet_isos, revert_etc):
		# Add our minimal pallet
		result = host.run(f'stack add pallet {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso')
		assert result.rc == 0

		# Make sure it made it to the DB
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

		# Sanity check that the pallet files got added to the filesystem
		assert host.file('/export/stack/pallets/minimal/1.0/sles12/sles/x86_64/roll-minimal.xml').exists

		# Now remove our test pallet
		result = host.run('stack remove pallet minimal')
		assert result.rc == 0

		# Should be gone from the DB
		result = host.run('stack list pallet minimal')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "minimal" argument is not a valid pallet
			[pallet ...] {expanded=bool} [arch=string] [os=string] [release=string] [version=string]
		''')

		# Directory should be gone as well
		assert not host.file('/export/stack/pallets/minimal/').exists

	def test_all_parameters(self, host, create_pallet_isos, revert_etc):
		# Add our minimal pallet
		result = host.run(f'stack add pallet {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso')
		assert result.rc == 0

		# Make sure it made it to the DB
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

		# Sanity check that the pallet files got added to the filesystem
		assert host.file('/export/stack/pallets/minimal/1.0/sles12/sles/x86_64/roll-minimal.xml').exists

		# Now remove our test pallet
		result = host.run('stack remove pallet minimal version=1.0 release=sles12 arch=x86_64 os=sles')
		assert result.rc == 0

		# Should be gone from the DB
		result = host.run('stack list pallet minimal')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "minimal" argument is not a valid pallet
			[pallet ...] {expanded=bool} [arch=string] [os=string] [release=string] [version=string]
		''')

		# Directory should be gone as well
		assert not host.file('/export/stack/pallets/minimal/').exists

	def test_no_arch_match(self, host, create_pallet_isos, revert_export_stack_pallets):
		# Add our minimal pallet
		result = host.run(f'stack add pallet {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso')
		assert result.rc == 0

		# Make sure it made it to the DB
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

		# Sanity check that the pallet files got added to the filesystem
		assert host.file('/export/stack/pallets/minimal/1.0/sles12/sles/x86_64/roll-minimal.xml').exists

		# Now run a remove command but pass an arch that won't match
		result = host.run('stack remove pallet minimal arch=x86')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "minimal" argument is not a valid pallet with parameters arch=x86
			{pallet ...} [arch=string] [os=string] [release=string] [run_hooks=bool] [version=string]
		''')

		# The pallet should still be in the DB
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

		# Pallet files should still exist as well
		assert host.file('/export/stack/pallets/minimal/1.0/sles12/sles/x86_64/roll-minimal.xml').exists

	def test_no_os_match(self, host, create_pallet_isos, revert_export_stack_pallets):
		# Add our minimal pallet
		result = host.run(f'stack add pallet {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso')
		assert result.rc == 0

		# Make sure it made it to the DB
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

		# Sanity check that the pallet files got added to the filesystem
		assert host.file('/export/stack/pallets/minimal/1.0/sles12/sles/x86_64/roll-minimal.xml').exists

		# Now run a remove command but pass an OS that won't match
		result = host.run('stack remove pallet minimal os=redhat')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "minimal" argument is not a valid pallet with parameters os=redhat
			{pallet ...} [arch=string] [os=string] [release=string] [run_hooks=bool] [version=string]
		''')

		# The pallet should still be in the DB
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

		# Pallet files should still exist as well
		assert host.file('/export/stack/pallets/minimal/1.0/sles12/sles/x86_64/roll-minimal.xml').exists

	def test_multiple_versions(self, host, create_pallet_isos, revert_etc, revert_export_stack_pallets):
		# Add our minimal pallet
		result = host.run(f'stack add pallet {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso')
		assert result.rc == 0

		# Make sure it made it to the DB
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

		# Sanity check that the pallet files got added to the filesystem
		assert host.file('/export/stack/pallets/minimal/1.0/sles12/sles/x86_64/roll-minimal.xml').exists

		# Now create a second version folder in the pallets directory,
		# to simulate multiple pallet versions
		result = host.run('mkdir /export/stack/pallets/minimal/2.0')
		assert result.rc == 0

		# Now remove our test pallet
		result = host.run('stack remove pallet minimal')
		assert result.rc == 0

		# Should be gone from the DB
		result = host.run('stack list pallet minimal')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "minimal" argument is not a valid pallet
			[pallet ...] {expanded=bool} [arch=string] [os=string] [release=string] [version=string]
		''')

		# The top level directory should still be there
		assert host.file('/export/stack/pallets/minimal/').exists

		# But the '1.0' version of the pallet should be gone
		assert not host.file('/export/stack/pallets/minimal/1.0').exists

	def test_remove_partially_removed_pallet(self, host, create_pallet_isos, revert_export_stack_pallets, revert_etc):
		# Add our minimal pallet
		result = host.run(f'stack add pallet {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso')
		assert result.rc == 0

		expected_pallet_info = [
			{
				'name': 'minimal',
				'version': '1.0',
				'release': 'sles12',
				'arch': 'x86_64',
				'os': 'sles',
				'boxes': ''
			}
		]

		# Make sure it made it to the DB
		result = host.run('stack list pallet minimal output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == expected_pallet_info

		# Sanity check that the pallet files got added to the filesystem
		assert host.file('/export/stack/pallets/minimal/1.0/sles12/sles/x86_64/roll-minimal.xml').exists

		# now kill part of the tree
		shutil.rmtree('/export/stack/pallets/minimal/1.0/sles12/sles/x86_64/')
		assert not host.file('/export/stack/pallets/minimal/1.0/sles12/sles/x86_64/roll-minimal.xml').exists

		# Make sure it is still in the DB
		result = host.run('stack list pallet minimal output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == expected_pallet_info

		# Now remove our test pallet
		result = host.run('stack remove pallet minimal')
		assert result.rc == 0

		# now it should be gone from DB and filesys
		result = host.run('stack list pallet minimal output-format=json')
		assert result.rc == 255
		assert result.stderr.startswith('error - "minimal" argument is not a valid pallet ')
		assert not host.file('/export/stack/pallets/minimal/').exists

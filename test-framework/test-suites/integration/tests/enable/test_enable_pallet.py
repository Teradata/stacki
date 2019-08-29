import json
from textwrap import dedent


class TestEnablePallet:
	def test_no_args(self, host):
		result = host.run('stack enable pallet')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "pallet" argument is required
			{pallet ...} [arch=string] [box=string] [os=string] [release=string] [version=string]
		''')

	def test_invalid_pallet(self, host):
		result = host.run('stack enable pallet test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid pallet with parameters arch=x86_64
			{pallet ...} [arch=string] [box=string] [os=string] [release=string] [version=string]
		''')

	def test_invalid_box(self, host):
		result = host.run('stack enable pallet test box=test')
		assert result.rc == 255
		assert result.stderr == 'error - unknown box "test"\n'

	def test_incompatable_os(self, host, create_pallet_isos):
		# Add the pallet that is ubuntu
		result = host.run(f'stack add pallet {create_pallet_isos}/test-different-os-1.0-prod.x86_64.disk1.iso')
		assert result.rc == 0

		# Try to enable it on our default box
		result = host.run(f'stack enable pallet test-different-os')
		assert result.rc == 255
		assert result.stderr == 'error - incompatible pallet "test-different-os" with OS "ubuntu"\n'
	
	def test_wrong_version(self, host, create_pallet_isos, revert_export_stack_pallets):
		# Add our test pallet
		result = host.run(f'stack add pallet {create_pallet_isos}/test-different-version-2.0-prod.x86_64.disk1.iso')
		assert result.rc == 0 

		# Try to enable it with the version parameter being wrong
		result = host.run(f'stack enable pallet test-different-version version=1.0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test-different-version" argument is not a valid pallet with parameters version=1.0, arch=x86_64
			{pallet ...} [arch=string] [box=string] [os=string] [release=string] [version=string]
		''')

	def test_default_box(self, host, host_os, create_pallet_isos, revert_etc, revert_export_stack_pallets):
		# Add our test pallet
		result = host.run(f'stack add pallet {create_pallet_isos}/test_1-{host_os}-1.0-prod.x86_64.disk1.iso')
		assert result.rc == 0

		# Add the pallet to the default box
		result = host.run(f'stack enable pallet test_1-{host_os}')
		assert result.rc == 0

		# Confirm it is in the box now
		result = host.run(f'stack list pallet test_1-{host_os} output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'arch': 'x86_64',
				'boxes': 'default',
				'name': f'test_1-{host_os}',
				'os': host_os,
				'release': 'prod',
				'version': '1.0'
			}
		]

	def test_with_box(self, host, host_os, create_pallet_isos, revert_etc, revert_export_stack_pallets):
		# Add our test box
		result = host.run('stack add box test')
		assert result.rc == 0

		# Add our test pallet
		result = host.run(f'stack add pallet {create_pallet_isos}/test_1-{host_os}-1.0-prod.x86_64.disk1.iso')
		assert result.rc == 0

		# Add the pallet to the test box
		result = host.run(f'stack enable pallet test_1-{host_os} box=test')
		assert result.rc == 0

		# Confirm it is in the box now
		result = host.run(f'stack list pallet test_1-{host_os} output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'arch': 'x86_64',
				'boxes': 'test',
				'name': f'test_1-{host_os}',
				'os': host_os,
				'release': 'prod',
				'version': '1.0'
			}
		]

	def test_already_enabled(self, host, host_os, create_pallet_isos, revert_etc, revert_export_stack_pallets):
		# Add our test pallet
		result = host.run(f'stack add pallet {create_pallet_isos}/test_1-{host_os}-1.0-prod.x86_64.disk1.iso')
		assert result.rc == 0

		# Add the pallet to the default box
		result = host.run(f'stack enable pallet test_1-{host_os}')
		assert result.rc == 0

		# Confirm it is in the box now
		result = host.run(f'stack list pallet test_1-{host_os} output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'arch': 'x86_64',
				'boxes': 'default',
				'name': f'test_1-{host_os}',
				'os': host_os,
				'release': 'prod',
				'version': '1.0'
			}
		]

		# Now enable it again, nothing should change in the db
		result = host.run(f'stack enable pallet test_1-{host_os}')
		assert result.rc == 0

		# Confirm everything is the same
		result = host.run(f'stack list pallet test_1-{host_os} output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'arch': 'x86_64',
				'boxes': 'default',
				'name': f'test_1-{host_os}',
				'os': host_os,
				'release': 'prod',
				'version': '1.0'
			}
		]

import json
from textwrap import dedent

import pytest


@pytest.mark.usefixtures('create_pallet_isos')
class TestDisablePallet:
	def test_disable_pallet_no_args(self, host):
		result = host.run('stack disable pallet')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "pallet" argument is required
			{pallet ...} [arch=string] [box=string] [os=string] [release=string] [version=string]
		''')

	def test_disable_pallet_invalid_pallet(self, host):
		result = host.run('stack disable pallet test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid pallet
			{pallet ...} [arch=string] [box=string] [os=string] [release=string] [version=string]
		''')

	def test_disable_pallet_invalid_box(self, host):
		result = host.run('stack disable pallet test box=test')
		assert result.rc == 255
		assert result.stderr == 'error - unknown box "test"\n'

	def test_disable_pallet_default_box(self, host, host_os):
		# Add our test pallet
		result = host.run(f'stack add pallet /export/test-files/pallets/test_1-{host_os}-1.0-prod.x86_64.disk1.iso')
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

		# Disable the pallet
		result = host.run(f'stack disable pallet test_1-{host_os}')
		assert result.rc == 0

		# Confirm it isn't in the box now
		result = host.run(f'stack list pallet test_1-{host_os} output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'arch': 'x86_64',
				'boxes': '',
				'name': f'test_1-{host_os}',
				'os': host_os,
				'release': 'prod',
				'version': '1.0'
			}
		]

	def test_disable_pallet_with_box(self, host, host_os):
		# Add our test box
		result = host.run('stack add box test')
		assert result.rc == 0

		# Add our test pallet
		result = host.run(f'stack add pallet /export/test-files/pallets/test_1-{host_os}-1.0-prod.x86_64.disk1.iso')
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

		# Disable the pallet
		result = host.run(f'stack disable pallet test_1-{host_os} box=test')
		assert result.rc == 0

		# Confirm it isn't in the box now
		result = host.run(f'stack list pallet test_1-{host_os} output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'arch': 'x86_64',
				'boxes': '',
				'name': f'test_1-{host_os}',
				'os': host_os,
				'release': 'prod',
				'version': '1.0'
			}
		]

import json
from textwrap import dedent

import pytest


@pytest.mark.usefixtures('create_pallet_isos')
class TestListPallet:
	def test_invalid_pallet(self, host):
		result = host.run('stack list pallet test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid pallet
			[pallet ...] {expanded=bool} [arch=string] [os=string] [release=string] [version=string]
		''')

	def test_with_arch(self, host):
		# Add our pallet with a unique arch
		result = host.run('stack add pallet /export/test-files/pallets/test-different-arch-1.0-prod.arm.disk1.iso')
		assert result.rc == 0

		# Make sure our list command filters by arch
		result = host.run('stack list pallet arch=arm output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'arch': 'arm',
				'boxes': '',
				'name': 'test-different-arch',
				'os': 'sles',
				'release': 'prod',
				'version': '1.0'
			}
		]

	def test_with_os(self, host):
		# Add our pallet with a unique os
		result = host.run('stack add pallet /export/test-files/pallets/test-different-os-1.0-prod.x86_64.disk1.iso')
		assert result.rc == 0

		# Make sure our list command filters by OS
		result = host.run('stack list pallet os=ubuntu output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'arch': 'x86_64',
				'boxes': '',
				'name': 'test-different-os',
				'os': 'ubuntu',
				'release': 'prod',
				'version': '1.0'
			}
		]

	def test_with_release(self, host):
		# Add our pallet with a unique release
		result = host.run('stack add pallet /export/test-files/pallets/test-different-release-1.0-test.x86_64.disk1.iso')
		assert result.rc == 0

		# Make sure our list command filters by release
		result = host.run('stack list pallet release=test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'arch': 'x86_64',
				'boxes': '',
				'name': 'test-different-release',
				'os': 'sles',
				'release': 'test',
				'version': '1.0'
			}
		]

	def test_with_version(self, host):
		# Add our pallet with a unique version
		result = host.run('stack add pallet /export/test-files/pallets/test-different-version-2.0-prod.x86_64.disk1.iso')
		assert result.rc == 0

		# Make sure our list command filters by arch
		result = host.run('stack list pallet version=2.0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'arch': 'x86_64',
				'boxes': '',
				'name': 'test-different-version',
				'os': 'sles',
				'release': 'prod',
				'version': '2.0'
			}
		]

	def test_with_expanded(self, host):
		# Add our pallet with a unique version
		result = host.run('stack add pallet /export/test-files/pallets/minimal-1.0-sles12.x86_64.disk1.iso')
		assert result.rc == 0

		# Make sure our list command filters by arch
		result = host.run('stack list pallet minimal expanded=true output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'arch': 'x86_64',
				'boxes': '',
				'name': 'minimal',
				'os': 'sles',
				'release': 'sles12',
				'url': '/export/test-files/pallets/minimal-1.0-sles12.x86_64.disk1.iso',
				'version': '1.0'
			}
		]

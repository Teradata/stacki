import json
from textwrap import dedent


class TestDisablePallet:
	def test_disable_pallet_no_args(self, host):
		result = host.run('stack disable pallet')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "pallet" argument is required
			{pallet ...} [arch=string] [box=string] [release=string] [version=string]
		''')

	def test_disable_pallet_invalid_pallet(self, host):
		result = host.run('stack disable pallet test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid pallet
			{pallet ...} [arch=string] [box=string] [release=string] [version=string]
		''')

	def test_disable_pallet_invalid_box(self, host):
		result = host.run('stack disable pallet test box=test')
		assert result.rc == 255
		assert result.stderr == 'error - unknown box "test"\n'

	def test_disable_pallet_default_box(self, host):
		# Add our test pallet
		result = host.run('stack add pallet /export/test-files/pallets/minimal-1.0-sles12.x86_64.disk1.iso')
		assert result.rc == 0

		# Add the pallet to the default box
		result = host.run('stack enable pallet minimal')
		assert result.rc == 0

		# Confirm it is in the box now
		result = host.run('stack list pallet minimal output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'arch': 'x86_64',
				'boxes': 'default',
				'name': 'minimal',
				'os': 'sles',
				'release': 'sles12',
				'version': '1.0'
			}
		]

		# Disable the pallet
		result = host.run('stack disable pallet minimal')
		assert result.rc == 0

		# Confirm it isn't in the box now
		result = host.run('stack list pallet minimal output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'arch': 'x86_64',
				'boxes': '',
				'name': 'minimal',
				'os': 'sles',
				'release': 'sles12',
				'version': '1.0'
			}
		]

	def test_disable_pallet_with_box(self, host):
		# Add our test box
		result = host.run('stack add box test')
		assert result.rc == 0

		# Add our test pallet
		result = host.run('stack add pallet /export/test-files/pallets/minimal-1.0-sles12.x86_64.disk1.iso')
		assert result.rc == 0

		# Add the cart to the test box
		result = host.run('stack enable pallet minimal box=test')
		assert result.rc == 0

		# Confirm it is in the box now
		result = host.run('stack list pallet minimal output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'arch': 'x86_64',
				'boxes': 'test',
				'name': 'minimal',
				'os': 'sles',
				'release': 'sles12',
				'version': '1.0'
			}
		]

		# Disable the pallet
		result = host.run('stack disable pallet minimal box=test')
		assert result.rc == 0

		# Confirm it isn't in the box now
		result = host.run('stack list pallet minimal output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'arch': 'x86_64',
				'boxes': '',
				'name': 'minimal',
				'os': 'sles',
				'release': 'sles12',
				'version': '1.0'
			}
		]

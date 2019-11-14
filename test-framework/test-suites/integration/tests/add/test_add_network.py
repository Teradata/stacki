import json
from textwrap import dedent


class TestAddNetwork:
	def test_no_network(self, host):
		result = host.run('stack add network')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "network" argument is required
			{name} {address=string} {mask=string} [dns=boolean] [gateway=string] [mtu=string] [pxe=boolean] [zone=string]
		''')
	
	def test_multiple_networks(self, host):
		result = host.run('stack add network test1 test2')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "network" argument must be unique
			{name} {address=string} {mask=string} [dns=boolean] [gateway=string] [mtu=string] [pxe=boolean] [zone=string]
		''')
	
	def test_no_address(self, host):
		result = host.run('stack add network test mask=255.255.255.0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "address" parameter is required
			{name} {address=string} {mask=string} [dns=boolean] [gateway=string] [mtu=string] [pxe=boolean] [zone=string]
		''')

	def test_no_mask(self, host):
		result = host.run('stack add network test address=192.168.0.0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "mask" parameter is required
			{name} {address=string} {mask=string} [dns=boolean] [gateway=string] [mtu=string] [pxe=boolean] [zone=string]
		''')
	
	def test_space_in_network(self, host):
		result = host.run('stack add network "test network" address=192.168.0.0 mask=255.255.255.0')
		assert result.rc == 255
		assert result.stderr == 'error - network name must not contain a space\n'

	def test_invalid_mtu(self, host):
		result = host.run('stack add network test address=192.168.0.0 mask=255.255.255.0 mtu=test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "mtu" parameter must be an integer
			{name} {address=string} {mask=string} [dns=boolean] [gateway=string] [mtu=string] [pxe=boolean] [zone=string]
		''')

	def test_existing_network(self, host):
		result = host.run('stack add network private address=192.168.0.0 mask=255.255.255.0')
		assert result.rc == 255
		assert result.stderr == 'error - network "private" exists\n'

	def test_invalid_network(self, host):
		result = host.run('stack add network test address=321.0.0.0 mask=255.255.255.0')
		assert result.rc == 255
		assert result.stderr == 'error - 321.0.0.0/255.255.255.0 is not a valid network address and subnet mask combination\n'

	def test_minimal_params(self, host):
		# Add our network
		result = host.run('stack add network test address=192.168.0.0 mask=255.255.255.0')
		assert result.rc == 0
		
		# Check it made it in as expected
		result = host.run('stack list network test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'address': "192.168.0.0",
				'dns': False,
				'gateway': '',
				'mask': '255.255.255.0',
				'mtu': None,
				'network': 'test',
				'pxe': False,
				'zone': 'test'
			}
		]
	
	def test_all_params(self, host):
		# Add our network
		result = host.run(
			'stack add network test address=192.168.0.0 mask=255.255.255.0 '
			'dns=true gateway=192.168.0.1 mtu=4096 pxe=true zone=test.com'
		)
		assert result.rc == 0
		
		# Check it made it in as expected
		result = host.run('stack list network test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'address': "192.168.0.0",
				'dns': True,
				'gateway': '192.168.0.1',
				'mask': '255.255.255.0',
				'mtu': 4096,
				'network': 'test',
				'pxe': True,
				'zone': 'test.com'
			}
		]

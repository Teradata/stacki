import json
from textwrap import dedent


class TestAddApplianceRoute:
	def test_no_args(self, host):
		result = host.run('stack add appliance route')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "address" parameter is required
			{appliance} {address=string} {gateway=string} [netmask=string]
		''')
	
	def test_no_appliance(self, host):
		result = host.run('stack add appliance route address=192.168.0.2 gateway=192.168.0.1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "appliance" parameter is required
			{appliance} {address=string} {gateway=string} [netmask=string]
		''')
	
	def test_with_subnet(self, host):
		# Add the route
		result = host.run('stack add appliance route backend address=192.168.0.2 gateway=private')
		assert result.rc == 0

		# Check that it is there now
		result = host.run('stack list appliance route backend output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"appliance": "backend",
				"network": "192.168.0.2",
				"netmask": "255.255.255.255",
				"gateway": "",
				"subnet": "private",
				"interface": None
			}
		]

	def test_with_gateway(self, host):
		# Add the route
		result = host.run('stack add appliance route backend address=192.168.0.2 gateway=192.168.0.1 netmask=255.255.255.0')
		assert result.rc == 0

		# Check that it is there now
		result = host.run('stack list appliance route backend output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"appliance": "backend",
				"network": "192.168.0.2",
				"netmask": "255.255.255.0",
				"gateway": "192.168.0.1",
				"subnet": None,
				"interface": None
			}
		]
	
	def test_duplicate(self, host):
		# Add the route
		result = host.run('stack add appliance route backend address=192.168.0.2 gateway=192.168.0.1 netmask=255.255.255.0')
		assert result.rc == 0

		# Add it again and make sure it errors out
		result = host.run('stack add appliance route backend address=192.168.0.2 gateway=192.168.0.1 netmask=255.255.255.0')
		assert result.rc == 255
		assert result.stderr == 'error - route exists\n'

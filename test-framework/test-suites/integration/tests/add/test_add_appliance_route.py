import pytest
import json

class TestAddApplianceRoute:

	def test_add_appliance_route(self, host):

		result = host.run(f'stack add appliance route frontend address=0.0.0.0 gateway=private netmask=255.255.255.0 interface=eth1')
		assert result.rc == 0

		result = host.run(f'stack list appliance route output-format=json')
		assert result.rc == 0
		routes = json.loads(result.stdout)
		route =  {
				"appliance": "frontend",
				"network": "0.0.0.0",
				"netmask": "255.255.255.0",
				"gateway": "",
				"subnet": "private",
				"interface": "eth1"
			}
		assert route in routes

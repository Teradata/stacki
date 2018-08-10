import pytest
import json

class TestAddRoute:

	def test_add_route(self, host):

		result = host.run(f'stack add route address=0.0.0.0 gateway=private netmask=255.255.255.0 interface=eth1')
		assert result.rc == 0

		result = host.run(f'stack list route output-format=json')
		assert result.rc == 0
		routes = json.loads(result.stdout)
		route =  {
				"network": "0.0.0.0",
				"netmask": "255.255.255.0",
				"gateway": "",
				"subnet": "private",
				"interface": "eth1"
			}
		assert route in routes

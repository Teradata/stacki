import pytest
import json

class TestAddHostRoute:

	def test_add_host_route(self, host):

		result = host.run(f'stack add host route frontend-0-0 address=0.0.0.0 gateway=private netmask=255.255.255.0 interface=eth1')
		assert result.rc == 0

		result = host.run(f'stack list host route output-format=json')
		assert result.rc == 0
		routes = json.loads(result.stdout)
		route =  {
				"host": "frontend-0-0",
				"network": "0.0.0.0",
				"netmask": "255.255.255.0",
				"gateway": "",
				"subnet": "private",
				"interface": "eth1",
				"source": "H"
			}
		assert route in routes

import pytest
import json

class TestAddOsRoute:
	def test_single_arg(self, host):
		result = host.run(f'stack add os route redhat address=0.0.0.0 gateway=private netmask=255.255.255.0 interface=eth1')
		assert result.rc == 0

		result = host.run(f'stack list os route redhat output-format=json')
		assert result.rc == 0
		routes = json.loads(result.stdout)
		route =  {
				"os": "redhat",
				"network": "0.0.0.0",
				"netmask": "255.255.255.0",
				"gateway": "",
				"subnet": "private",
				"interface": "eth1"
			}
		assert route in routes

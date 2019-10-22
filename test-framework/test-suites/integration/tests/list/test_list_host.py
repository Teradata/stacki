import json


class TestListHost:
	def test_lookup_by_IP(self, host, add_host_with_interface, host_os):
		# Set an IP on the interface
		result = host.run('stack set host interface ip backend-0-0 interface=eth0 ip=192.168.1.1')
		assert result.rc == 0

		# List our host by IP
		result = host.run(f'stack list host 192.168.1.1 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'appliance': 'backend',
			'box': 'default',
			'comment': None,
			'environment': None,
			'host': 'backend-0-0',
			'installaction': 'default',
			'os': host_os,
			'osaction': 'default',
			'rack': '0',
			'rank': '0'
		}]

	def test_lookup_by_FQDN(self, host, add_host_with_interface, add_network, host_os):
		# Set the zone on the test network, and add our backend interface to it
		result = host.run('stack set network zone test zone=example.com')
		assert result.rc == 0

		result = host.run('stack set host interface network backend-0-0 interface=eth0 network=test')
		assert result.rc == 0

		# List our host by HOSTNAME.ZONE
		result = host.run(f'stack list host backend-0-0.example.com output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'appliance': 'backend',
			'box': 'default',
			'comment': None,
			'environment': None,
			'host': 'backend-0-0',
			'installaction': 'default',
			'os': host_os,
			'osaction': 'default',
			'rack': '0',
			'rank': '0'
		}]

	def test_lookup_by_FQDN_with_name(self, host, add_host_with_interface, add_network, host_os):
		# Set a name on the interface
		result = host.run('stack set host interface name backend-0-0 interface=eth0 name=test')
		assert result.rc == 0

		# Set the zone on the test network, and add our backend interface to it
		result = host.run('stack set network zone test zone=example.com')
		assert result.rc == 0

		result = host.run('stack set host interface network backend-0-0 interface=eth0 network=test')
		assert result.rc == 0

		# List our host by NAME.ZONE
		result = host.run(f'stack list host test.example.com output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'appliance': 'backend',
			'box': 'default',
			'comment': None,
			'environment': None,
			'host': 'backend-0-0',
			'installaction': 'default',
			'os': host_os,
			'osaction': 'default',
			'rack': '0',
			'rank': '0'
		}]

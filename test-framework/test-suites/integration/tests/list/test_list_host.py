import json
from textwrap import dedent


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

	def test_lookup_non_kickstartable(self, host, add_host, host_os):
		# Set the host to non-kickstartable
		result = host.run('stack set host attr backend-0-0 attr=kickstartable value=false')
		assert result.rc == 0

		# List the host
		result = host.run('stack list host backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'appliance': 'backend',
			'box': 'default',
			'comment': None,
			'environment': None,
			'host': 'backend-0-0',
			'installaction': None,
			'os': host_os,
			'osaction': None,
			'rack': '0',
			'rank': '0'
		}]

	def test_hosts_sorting(self, host, add_host):
		''' ensure that hosts are listed in the order expected '''
		host_data = [
			("ethernet-2-1"    , "2"         , "1"          , "switch"),
			("stacki-2-11"     , "2"         , "11"         , "backend"),
			("infiniband-2-18" , "2"         , "18"         , "switch"),
			("stacki-2-12"     , "2"         , "12"         , "backend"),
			("stacki-2-10"     , "2"         , "10"         , "backend"),
			("backend-1-0"     , "1"         , "station-11" , "backend"),
			("ethernet-2-43"   , "2"         , "43"         , "switch"),
			("backend-0-1"     , "sector-42" , "2"          , "backend"),
			("backend-0-3"     , "sector-42" , "4"          , "backend"),
			("backend-0-4"     , "sector-42" , "station-8"  , "backend"),
			("infiniband-2-20" , "2"         , "20"         , "switch"),
			("backend-0-2"     , "sector-42" , "3"          , "backend"),
		]

		# backend-0-0 and frontend-0-0 already added at test initialization...
		for host_tup in host_data:
			add_host(*host_tup)

		expected_host_output = dedent('''\
			frontend-0-0
			backend-0-0
			backend-1-0
			ethernet-2-1
			stacki-2-10
			stacki-2-11
			stacki-2-12
			infiniband-2-18
			infiniband-2-20
			ethernet-2-43
			backend-0-1
			backend-0-2
			backend-0-3
			backend-0-4
		''')

		result = host.run("stack list host | cut -d' ' -f1")
		assert result.rc == 0
		assert result.stdout == f'HOST\n{expected_host_output}'

		result = host.run('stack list host output-format=json')
		assert result.rc == 0
		hosts = [host['host'] for host in json.loads(result.stdout)]
		assert hosts == expected_host_output.strip().splitlines()
